from django.db import models


class TaskStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    STARTED = "started", "Started"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    FAILED = "failed", "Failed"


class SystemTaskExecution(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=255,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
    result = models.TextField(blank=True)
    error = models.TextField(blank=True)

    task_args = models.JSONField(default=dict)
    task_kwargs = models.JSONField(default=dict)

    retry_count = models.IntegerField(default=0)

    status = models.CharField(
        max_length=255,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )

    def __str__(self):
        return self.name
