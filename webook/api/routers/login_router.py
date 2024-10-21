from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth_superuser
from webook.api.jwt_auth import issue_token
from webook.api.schemas.base_schema import BaseSchema
from webook.api.models import ServiceAccount, APIEndpoint
from django.core.exceptions import PermissionDenied
from jwt import encode
from django.conf import settings
from datetime import datetime, timedelta, timezone
from django.conf import settings
from webook.users.models import User

login_router = Router(tags=["Login"])


class LoginSchema(BaseSchema):
    email: str
    password: str


@login_router.post("/login", response=str, auth=None)
def login_user_account(request, payload: LoginSchema) -> str:
    if not settings.ALLOW_EMAIL_LOGIN:
        raise PermissionDenied("Email login is disabled. Use SSO to obtain a token.")

    user_account = get_object_or_404(User, email=payload.email)

    if not user_account.check_password(payload.password):
        raise PermissionDenied("Invalid password")

    return encode(
        payload={
            "iss": "webook",
            "iat": datetime.now(timezone.utc),
            "aud": "webook",
            "sub": user_account.email,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.JWT_TOKEN_LIFETIME_MINUTES),
        },
        key=settings.SECRET_KEY,
        algorithm="HS256",
    )
