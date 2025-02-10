import json
from webook.systask.tasklib import AbstractTaskingScheduler
from django.conf import settings
import google.cloud.tasks_v2 as tasks_v2


class GoogleCloudTasksScheduler(AbstractTaskingScheduler):
    def __init__(self, project_id: str, location: str, queue: str):
        self.client = tasks_v2.CloudTasksClient()
        self.project_id = project_id
        self.location = location
        self.queue = queue

    def send_task(self, task_id: int):
        task = tasks_v2.Task(
            http_request=tasks_v2.HttpRequest(
                url=f"{settings.APP_URL.replace('http', 'https')}/api/systask/{task_id}/executeTask",
                http_method=tasks_v2.HttpMethod.POST,
                headers={"Content-type": "application/json"},
                oidc_token=tasks_v2.OidcToken(
                    service_account_email=settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_EMAIL,
                    audience=settings.GOOGLE_CLOUD_SERVICE_ACCOUNT_AUDIENCE,
                ),
            ),
            name=self.client.task_path(
                self.project_id, self.location, self.queue, task_id
            ),
        )
        task = self.client.create_task(
            request={
                "parent": self.client.queue_path(
                    self.project_id, self.location, self.queue
                ),
                "task": task,
            }
        )

        return task
