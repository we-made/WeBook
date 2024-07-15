from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class RevokedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    revoked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class APIEndpoint(models.Model):
    operation_id = models.CharField(max_length=255, unique=True)
    path = models.CharField(max_length=255)

    def __str__(self):
        return self.operation_id


class ServiceAccount(AbstractUser):
    valid_until = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    allowed_endpoints = models.ManyToManyField(
        APIEndpoint, related_name="service_accounts"
    )

    groups = None
    user_permissions = None

    class Meta:
        verbose_name = "Service Account"
        verbose_name_plural = "Service Accounts"

    def clean(self):
        super().clean()
        raise ValidationError(
            _("Service accounts cannot be used for login on the default login page.")
        )
