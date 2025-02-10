from ninja.router import Router

systask_router = Router(tags=["System Task"])

from webook.api.schemas.base_schema import BaseSchema
from django.apps.registry import Apps
from .tasklib import get_all_tasks, get_task
from webook.systask.models import SystemTaskExecution, TaskStatus
import google.cloud.tasks_v2 as tasks_v2
from django.conf import settings
from ninja.errors import HttpError
from webook.systask.redlock_factory import get_redlock_factory
from webook.systask.tasklib import TaskManager
from webook.systask.task_manager_factory import (
    create_task_manager,
    TaskManagerSchedulerProvider,
)


class EnqueueTaskSchema(BaseSchema):
    task_name: str
    task_args: dict
    task_kwargs: dict


class ExecuteTaskSchema(BaseSchema):
    task_args: dict
    task_kwargs: dict


@systask_router.post("/enqueueTask")
def enqueue_task(request, payload: EnqueueTaskSchema):
    task_manager = create_task_manager()
    ste: SystemTaskExecution = task_manager.enqueue_task(
        payload.task_name, payload.task_args, payload.task_kwargs
    )

    return {"task_id": ste.id}


@systask_router.post("/{task_id}/executeTask")
def execute_task(request, payload: ExecuteTaskSchema, task_id: str):
    task_manager = create_task_manager()
    ste: SystemTaskExecution = task_manager.execute_task(task_id)

    return {"status": ste.status}


@systask_router.post("/{task_id}/cancelTask")
def cancel_task(request, task_id: int):
    task_manager = create_task_manager()
    ste: SystemTaskExecution = task_manager.cancel_task(task_id)

    return {"status": ste.status}


@systask_router.post("/{task_id}/getStatus")
def get_task_status(request, task_id: str):
    task = SystemTaskExecution.objects.get(id=task_id)
    return task.status


@systask_router.get("/getTaskTypes")
def get_task_list(request):
    return list(get_all_tasks().keys())
