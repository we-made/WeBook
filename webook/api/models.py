from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import Group
from webook.users.models import User


class RevokedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    revoked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class APIScope(models.Model):
    disabled = models.BooleanField(default=False)
    operation_id = models.CharField(max_length=255, unique=True)
    path = models.CharField(max_length=255)

    groups_allowed = models.ManyToManyField(Group, related_name="endpoint_scopes")
    users_directly_allowed = models.ManyToManyField(
        User, related_name="endpoint_scopes"
    )

    def __str__(self):
        return self.operation_id


class ServiceAccount(AbstractUser):
    person = models.ForeignKey(
        "arrangement.Person",
        on_delete=models.RESTRICT,
        related_name="service_accounts",
        null=True,
        blank=True,
    )

    NORMAL_SERVICE_ACCOUNT = "normal"
    GOOGLE_SERVICE_ACCOUNT = "google"
    SERVICE_ACCOUNT_TYPES = [
        (NORMAL_SERVICE_ACCOUNT, "Normal"),
        (GOOGLE_SERVICE_ACCOUNT, "Google"),
    ]

    service_account_type = models.CharField(
        max_length=255, choices=SERVICE_ACCOUNT_TYPES, default=NORMAL_SERVICE_ACCOUNT
    )   

    valid_until = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    allowed_endpoints = models.ManyToManyField(
        APIScope, related_name="service_accounts"
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=(
            "The groups this service account belongs to. A service account will get all API scopes "
            "granted to each of their groups."
        ),
        related_name="service_accounts_set",
        related_query_name="service_account",
    )
    user_permissions = None

    class Meta:
        verbose_name = "Service Account"
        verbose_name_plural = "Service Accounts"

    def clean(self):
        super().clean()
        raise ValidationError(
            "Service accounts cannot be used for login on the default login page."
        )

class LoginRecord(models.Model):
    service_account = models.ForeignKey(
        ServiceAccount, on_delete=models.RESTRICT, related_name="login_records"
    )
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    class Meta:
        verbose_name = "Login Record"
        verbose_name_plural = "Login Records"

    def __str__(self):
        return self.service_account.email