from enum import Enum
from django.conf import settings

from webook.systask.schedulers.google_cloud_tasks_scheduler import (
    GoogleCloudTasksScheduler,
)
from webook.systask.tasklib import TaskManager


class TaskManagerSchedulerProvider(Enum):
    GOOGLE_CLOUD_TASKS = "google_cloud_tasks"


def create_task_manager():
    provider = settings.SYSTASK_SCHEDULER_PROVIDER
    if provider == "google_cloud_tasks":
        return TaskManager(
            task_scheduler=GoogleCloudTasksScheduler(
                project_id=settings.GOOGLE_CLOUD_PROJECT_ID,
                location=settings.GOOGLE_CLOUD_LOCATION,
                queue=settings.GOOGLE_CLOUD_QUEUE,
            )
        )
    else:
        raise ValueError("Invalid task manager provider")
