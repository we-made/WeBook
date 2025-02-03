from enum import Enum
from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth_superuser
from webook.api.jwt_auth import IssueeType, TokenType, issue_token
from webook.api.schemas.base_schema import BaseSchema
from webook.api.models import ServiceAccount, APIScope
from django.core.exceptions import PermissionDenied
from jwt import encode
from django.conf import settings
from webook.api.models import LoginRecord
from datetime import datetime, timedelta, timezone
import secrets

from webook.api.scopes_router import APIScopeGetSchema

service_account_router = Router(tags=["Service Account"])


class ServiceAccountTypeOptions(Enum):
    GOOGLE_SERVICE_ACCOUNT = "google"
    SERVICE_ACCOUNT = "normal"


class ServiceAccountSchema(BaseSchema):
    id: int
    username: str
    is_active: bool
    allowed_endpoints: List[APIScopeGetSchema]
    last_seen: Optional[datetime] = None
    service_account_type: ServiceAccountTypeOptions


class CreateServiceAccountSchema(BaseSchema):
    username: str
    password: Optional[str]


class CreateGoogleServiceAccountSchema(BaseSchema):
    email: str


class UpdateServiceAccountSchema(BaseSchema):
    is_deactivated: Optional[bool] = False
    allowed_endpoints: Optional[List[str]] = None


class ServiceAccountLoginSchema(BaseSchema):
    username: str
    password: str


class ServiceAccountLoginResponse(BaseSchema):
    token: str


@service_account_router.post("/login", response=str, auth=None)
def login_service_account(request, payload: ServiceAccountLoginSchema) -> str:
    service_account = get_object_or_404(ServiceAccount, username=payload.username)

    if service_account.is_deactivated:
        raise PermissionDenied("Service account is deactivated")

    if (
        service_account.service_account_type
        == ServiceAccountTypeOptions.GOOGLE_SERVICE_ACCOUNT.value
    ):
        raise PermissionDenied(
            "Invalid username"
        )  # Google service accounts cannot be logged in with a password

    if not payload.password:
        raise PermissionDenied("Invalid password")

    if not service_account.check_password(payload.password):
        raise PermissionDenied("Invalid password")

    record = LoginRecord(
        service_account=service_account,
        login_time=datetime.now(timezone.utc),
        ip_address=(
            request.META.get("REMOTE_ADDR")
            if "X-Forwarded-For" not in request.META
            else request.META.get("X-Forwarded-For")
        ),
    )
    record.save()

    return issue_token(
        issuee_type=IssueeType.ServiceAccount,
        pk=service_account.id,
        token_type=TokenType.Access,
    )


@service_account_router.get(
    "/", response=List[ServiceAccountSchema], auth=django_auth_superuser
)
def list_service_accounts(request) -> List[ServiceAccountSchema]:
    return ServiceAccount.objects.all()


@service_account_router.post(
    "/", response=ServiceAccountSchema, auth=django_auth_superuser
)
def create_service_account(
    request, payload: CreateServiceAccountSchema
) -> ServiceAccountSchema:
    if ServiceAccount.objects.filter(username=payload.username).exists():
        raise PermissionDenied("Service account with this username already exists")

    service_account = ServiceAccount(username=payload.username)
    service_account.set_password(payload.password)

    service_account.save()

    return service_account


@service_account_router.post(
    "/google", response=ServiceAccountSchema, auth=django_auth_superuser
)
def create_google_service_account(
    request, payload: CreateGoogleServiceAccountSchema
) -> ServiceAccountSchema:
    if ServiceAccount.objects.filter(email=payload.email).exists():
        raise PermissionDenied("Service account with this email already exists")

    service_account = ServiceAccount(
        username=payload.email.split("@")[0],
        email=payload.email,
    )
    service_account.set_password(secrets.token_urlsafe(32))
    service_account.service_account_type = (
        ServiceAccountTypeOptions.GOOGLE_SERVICE_ACCOUNT.value
    )

    service_account.save()

    return service_account


@service_account_router.get("/ep", response=List[str])
def get_endpoint_choices(request):
    return list(APIScope.objects.values_list("operation_id", flat=True))


@service_account_router.get(
    "/{service_account_id}", response=ServiceAccountSchema, auth=django_auth_superuser
)
def get_service_account(request, service_account_id: int):
    return get_object_or_404(ServiceAccount, pk=service_account_id)


@service_account_router.put(
    "update/{service_account_id}",
    response=ServiceAccountSchema,
    auth=django_auth_superuser,
)
def update_service_account(
    request, service_account_id: int, payload: UpdateServiceAccountSchema
) -> ServiceAccountSchema:
    service_account = get_object_or_404(ServiceAccount, pk=service_account_id)

    if payload.is_deactivated:
        service_account.is_deactivated = True
    if payload.allowed_endpoints is not None:
        service_account.allowed_endpoints.set(
            APIScope.objects.filter(operation_id__in=payload.allowed_endpoints)
        )

    service_account.save()

    return service_account
