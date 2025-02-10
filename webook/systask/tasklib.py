from datetime import timezone
import json
from typing import Callable, Optional
from django.conf import settings
import redlock
import google.cloud.tasks_v2 as tasks_v2
from webook.systask.models import SystemTaskExecution, TaskStatus
from abc import ABC, abstractmethod

MAX_RETRIES_BEFORE_FAIL = 3


def get_redlock_factory() -> redlock.RedLockFactory:
    """Get a RedLockFactory instance for distributed locking.

    Returns:
        redlock.RedLockFactory: A RedLockFactory instance.
    """
    return redlock.RedLockFactory(
        connection_details=[
            {"host": settings.REDIS_URL.replace("redis://", "").split(":")[0]}
        ]
    )


__TASKS = {}


def systask(func):
    __TASKS[func.__name__] = func

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def get_task(task_name: str) -> Optional[Callable]:
    return __TASKS.get(task_name)


def get_all_tasks():
    return __TASKS


class TaskNotFoundError(Exception):
    """Exception raised when a task is not found."""

    pass


class TaskExecutionFailedError(Exception):
    """Exception raised when a task execution fails."""

    inner_exception: Exception

    def __str__(self):
        return f"Task execution failed: {self.inner_exception}"


class TaskAlreadyRunningError(Exception):
    """Exception raised when a task is already running."""

    pass


class TaskNotPendingExecutionError(Exception):
    """Exception raised when a task that is not pending is attempted to be executed."""

    pass


class AbstractTaskingScheduler(ABC):
    @abstractmethod
    def send_task(self, task_id: int):
        pass


class TaskManager:
    def __init__(self, task_scheduler: AbstractTaskingScheduler):
        if not task_scheduler:
            raise ValueError("You must provide a task scheduler")

        self.task_scheduler = task_scheduler

    def enqueue_task(
        self, task_name: str, task_args: dict, task_kwargs: dict
    ) -> SystemTaskExecution:
        task_func = get_task(task_name)

        if not task_func:
            raise ValueError("Task type not found")

        task = SystemTaskExecution.objects.create(
            name=task_name, task_args=task_args, task_kwargs=task_kwargs
        )
        task.save()

        _ = self.task_scheduler.send_task(
            task_id=task.id,
        )

        return task

    def execute_task(self, task_id: str) -> SystemTaskExecution:
        task = SystemTaskExecution.objects.get(id=task_id)
        task_func: Callable = get_task(task.name)

        if not task_func:
            task.error = "Task type was not found"
            return {"error": "Task type not found"}

        if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
            return {
                "error": "Task is not in a pending or retryable state, and can as such not be executed"
            }

        if (
            task.status == TaskStatus.FAILED
            and task.retry_count >= MAX_RETRIES_BEFORE_FAIL
        ):
            task.error = "Task has failed too many times, and will not be retried"
            task.status = TaskStatus.FAILED
            task.save()
            return {"error": "Task has failed too many times, and will not be retried"}

        with get_redlock_factory().create_lock(f"task:{task.id}", 5000):
            try:
                task.status = TaskStatus.STARTED
                task.started_at = timezone.now()
                task.save()

                task_result = task_func(*task.task_args, **task.task_kwargs)
                if task_result:
                    try:
                        task.result = json.dumps(task_result)
                    except Exception as e:
                        task.result = f"Unable to serialize task result: {str(e)}"

                task.completed_at = timezone.now()
                task.status = TaskStatus.COMPLETED
                task.save()
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                task.retry_count += 1
                task.save()
                raise TaskExecutionFailedError(e)

            return task

    def cancel_task(self, task_id: str) -> SystemTaskExecution:
        task = SystemTaskExecution.objects.get(id=task_id)

        if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
            raise ValueError(
                "Task is not in a pending or failed state, and can as such not be cancelled"
            )

        task.cancelled_at = timezone.now()
        task.status = TaskStatus.CANCELLED
        task.save()
        return task
