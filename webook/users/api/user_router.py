from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http.client import HTTPException
import logging
from typing import List, Optional, Union
from django.http import HttpResponse
from ninja import NinjaAPI
from pydantic import EmailStr, SecretStr
import sentry_sdk
from webook.api.jwt_auth import (
    IssueeType,
    JWTBearer,
    TokenData,
    decode_jwt_token,
    issue_token,
)
from ninja.security import django_auth
from webook.api.models import APIScope, ServiceAccount
from webook.api.routers.service_account_router import ServiceAccountSchema
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.crud_router import CrudRouter, Views
from django.db.models import QuerySet

from webook.api.scopes_router import APIScopeGetSchema
from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.arrangement.models import Person
from webook.users.models import LoginAudit, User, UserTokenRevocation
from django.conf import settings
from allauth.account.models import Login
from allauth.account.internal import flows
from allauth.account import app_settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from ninja.throttling import AnonRateThrottle
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import Group

from webook.users.utils.password_reset import (
    complete_password_reset_request,
    perform_password_reset_request,
)


class GroupRouter(CrudRouter):
    def __init__(self, *args, **kwargs):
        self.non_deferred_fields = ["endpoint_scopes"]
        super().__init__(*args, **kwargs)

    def get_queryset(self, view: Views = Views.GET) -> QuerySet:
        qs = super().get_queryset(view)
        qs = qs.prefetch_related("endpoint_scopes")
        return qs


class GroupGetSchema(BaseSchema):
    name: str
    endpoint_scopes: List[APIScopeGetSchema]
    user_set: List[UserGetSchema]
    service_accounts_set: List[ServiceAccountSchema]


class GroupUpdatePermissionsSchema(BaseSchema):
    group_name: str
    endpoint_scopes: List[str]


group_router = GroupRouter(
    model=Group,
    tags=["Group"],
    views=[Views.GET, Views.LIST],
    get_schema=GroupGetSchema,
    list_schema=GroupGetSchema,
)


@group_router.post("/create")
def create_group(request, name: str):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    group = Group(name=name)
    group.save()

    return {"success": True}


@group_router.delete("/delete")
def delete_group(request, name: str):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    group = Group.objects.get(name=name)
    group.delete()

    return {"success": True}


@group_router.post("/update-scopes")
def update_group_permissions(request, data: GroupUpdatePermissionsSchema):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    group = Group.objects.get(name=data.group_name)
    group.endpoint_scopes.clear()

    for endpoint in data.endpoint_scopes:
        try:
            ep = APIScope.objects.get(operation_id=endpoint)
            group.endpoint_scopes.add(ep.id)
        except APIScope.DoesNotExist:
            raise HTTPException(
                status_code=400, detail=f"Endpoint {endpoint} does not exist"
            )

    group.save()

    return {"success": True}


@group_router.post("/add-user-to-group")
def add_user_to_group(request, group_name: str, user_id: int):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    try:
        group = Group.objects.get(name=group_name)
        user = User.objects.get(pk=user_id)
    except Group.DoesNotExist:
        raise HTTPException(status_code=404, detail="Group not found")
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    user.groups.add(group)
    user.save()

    return {"success": True}


@group_router.post("/remove-user-from-group")
def remove_user_from_group(request, group_name: str, user_id: int):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    try:
        group = Group.objects.get(name=group_name)
        user = User.objects.get(pk=user_id)
    except Group.DoesNotExist:
        raise HTTPException(status_code=404, detail="Group not found")
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    user.groups.remove(group)
    user.save()

    return {"success": True}


@group_router.post("/add-service-account-to-group")
def add_service_account_to_group(request, group_name: str, service_account_id: int):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    try:
        group = Group.objects.get(name=group_name)
        service_account = ServiceAccount.objects.get(pk=service_account_id)
    except Group.DoesNotExist:
        raise HTTPException(status_code=404, detail="Group not found")
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service account not found")

    service_account.groups.add(group)
    service_account.save()

    return {"success": True}


@group_router.post("/remove-service-account-from-group")
def remove_service_account_from_group(
    request, group_name: str, service_account_id: int
):
    if not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    try:
        group = Group.objects.get(name=group_name)
        service_account = ServiceAccount.objects.get(pk=service_account_id)
    except Group.DoesNotExist:
        raise HTTPException(status_code=404, detail="Group not found")
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="Service account not found")

    service_account.groups.remove(group)
    service_account.save()

    return {"success": True}


class UserGetSchema(BaseSchema):
    email: str
    timezone: str
    is_user_admin: bool
    # profile_picture: str
    person: PersonGetSchema
    groups: List[GroupGetSchema]


class RegisterUserSchema(BaseSchema):
    email: EmailStr
    password: SecretStr

    first_name: str
    last_name: str


class ChangePasswordSchema(BaseSchema):
    email: EmailStr
    token: str
    new_password: SecretStr
    # Super user can override / skip token validation process.
    # Will have no effect if the user is not a super user.
    super_user_override_token_validation: bool = False


class RefreshTokenRefreshSchema(BaseSchema):
    refresh_token: str


class RefreshTokenRefreshResponseSchema(BaseSchema):
    access_token: str
    refresh_token: str


class EmailLoginSchema(BaseSchema):
    email: EmailStr
    password: SecretStr
    remember: Optional[bool] = False
    get_cookie: Optional[bool] = False


class UserRouter(CrudRouter):
    def __init__(self, *args, **kwargs):
        self.non_deferred_fields = ["person"]
        super().__init__(*args, **kwargs)

    def get_queryset(self, view: Views = Views.GET) -> QuerySet:
        qs = super().get_queryset(view)
        qs = qs.select_related("person")
        return qs


router = UserRouter(
    model=User,
    tags=["User"],
    views=[Views.GET, Views.LIST],
    get_schema=UserGetSchema,
    list_schema=UserGetSchema,
)


def _throw_if_email_login_not_allowed():
    if not settings.ALLOW_EMAIL_LOGIN:
        raise HTTPException(status_code=403, detail="Email login is not allowed")


@router.get(
    "/me/",
    response=Union[UserGetSchema, ServiceAccountSchema],
    auth=[JWTBearer(require_scoped_access=False), django_auth],
)
def me(request):
    if request.auth:
        return request.auth
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post("/register", throttle=[AnonRateThrottle("10/h")])
def register_user(request, data: RegisterUserSchema):
    if not settings.ALLOW_EMAIL_LOGIN:
        raise HTTPException(
            status_code=403,
            detail="Email login disabled. Normal registration is not allowed.",
        )

    if not settings.ACCOUNT_ALLOW_REGISTRATION and not request.auth.is_superuser:
        raise HTTPException(
            status_code=403, detail="Registration is not allowed on this instance."
        )

    user = User.objects.create_user(
        email=data.email,
        password=data.password.get_secret_value(),
    )

    person = Person.objects.create(
        first_name=data.first_name,
        last_name=data.last_name,
    )

    user.save()
    person.save()
    user.person = person
    user.save()

    return user


@router.post("/email-login", auth=None)
def email_login(request, data: EmailLoginSchema, request_refresh_token: bool = False):
    _throw_if_email_login_not_allowed()

    login_audit = LoginAudit(
        attempted_email=data.email,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
    )

    failed_attempts_last_hour_count = LoginAudit.objects.filter(
        ip_address=login_audit.ip_address,
        time_stamp__gte=datetime.now(timezone.utc) - timedelta(hours=1),
        successful=False,
    ).count()

    if failed_attempts_last_hour_count >= 10:
        login_audit.successful = False
        login_audit.threshold_exceeded = True
        login_audit.save()
        logging.warning(
            f"Attempted logins on {login_audit.attempted_email} has exceeded login threshold of 10 failed attempts."
        )
        sentry_sdk.capture_message(
            "Failed logins threshold exceeded for email login. Email: {login_audit.attempted_email}. Attempts should be reviewed.",
        )

        return HttpResponse(status=429)

    user = authenticate(email=data.email, password=data.password.get_secret_value())

    if user is None:
        login_audit.successful = False
        login_audit.save()
        return HttpResponse(status=401)

    token = issue_token(
        issuee_type=IssueeType.User,
        pk=user.pk,
    )

    login_audit.successful = True
    login_audit.user = user
    login_audit.save()

    return {"access_token": token}


@router.post("/refresh-token-refresh")
def refresh_token_refresh(request, data: RefreshTokenRefreshSchema):
    """Refresh a refresh token.
    This will place a revocation on all tokens issued before the current time.
    """
    t: TokenData = decode_jwt_token(data.refresh_token)

    if t.token_type != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")

    if t.issuee_type != IssueeType.User:
        raise HTTPException(status_code=400, detail="Invalid issuee type")

    user = User.objects.get(pk=t.pk)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    # revoke all prior tokens to this point - for the user
    revocation = UserTokenRevocation(
        user=user,
        revocation_reason="Token refresh",
    )
    revocation.save()

    access_token = issue_token(
        issuee_type=IssueeType.User,
        pk=user.pk,
        token_type="access",
    )
    new_refresh_token = issue_token(
        issuee_type=IssueeType.User,
        pk=user.pk,
        token_type="refresh",
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
    }


@router.post("/revoke-all-tokens-on-user")
def revoke_all_tokens_on_user(request, user_id: int):
    current_user = request.auth

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    user = User.objects.get(pk=user_id)

    revocation = UserTokenRevocation(
        user=user,
        revocation_reason="Admin action",
    )

    revocation.save()

    return {"revoked": True}


@router.post(
    "/revoke-all-user-tokens",
    auth=JWTBearer(require_scoped_access=True, super_user_only=True),
)
def revoke_all_user_tokens(request):
    """Revoke all tokens for all users in the system. Superuser only."""
    current_user = request.auth

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    for user in User.objects.all():
        revocation = UserTokenRevocation(
            user=user,
            revocation_reason="Admin action",
        )

        revocation.save()

    return {"revoked": True}


@router.post(
    "/me/revoke-all-tokens", auth=[JWTBearer(require_scoped_access=False), django_auth]
)
def revoke_all_tokens(request):
    """Revoke all tokens for the current user."""
    user = request.auth

    revocation = UserTokenRevocation(
        user=user,
        revocation_reason="User action",
    )

    revocation.save()

    return {"revoked": True}


@router.post("/ms-login")
def ms_login():
    if not settings.ALLOW_SSO:
        raise HTTPException(
            status_code=403, detail="SSO login is not allowed on this instance."
        )


@router.post("/logout", auth=[JWTBearer(require_scoped_access=False), django_auth])
def logout(request):
    UserTokenRevocation(
        user=request.auth,
        revocation_reason="User action",
    ).save()

    return {"revoked": True}


@router.post("/trigger-forgot-password", throttle=[AnonRateThrottle("10/h")], auth=None)
def forgot_password(request, email: EmailStr):
    _throw_if_email_login_not_allowed()

    user = User.objects.filter(email=email).first()

    if user is None:
        return {"success": True}

    site = get_current_site(request)
    perform_password_reset_request(
        user=user,
        domain=site.domain,
        site_name=site.name,
    )

    return {"success": True}


@router.post("/change-password", throttle=[AnonRateThrottle("10/h")], auth=None)
def change_password(request, data: ChangePasswordSchema):
    user = User.objects.filter(email=data.email).first()
    if user is None:
        return {"success": False}

    if request.auth.is_superuser and data.super_user_override_token_validation:
        user.set_password(data.new_password.get_secret_value())
        return {"success": True, "super_user_override": True}

    try:
        complete_password_reset_request(
            user=user,
            code=data.token,
            new_password=data.new_password.get_secret_value(),
        )
    except ValueError as e:
        logging.info(f"Failed to reset password: {e}")
        return {"success": False}

    UserTokenRevocation(
        user=user,
        revocation_reason="Password reset",
    ).save()

    return {"success": True}
