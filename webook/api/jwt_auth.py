from datetime import datetime, timedelta, timezone
import logging
from ninja.security import HttpBearer
from webook.api.models import ServiceAccount, RevokedToken, APIEndpoint
from django.conf import settings
from jwt import ExpiredSignatureError, decode, DecodeError, encode
from ninja.errors import HttpError
from asgiref.sync import sync_to_async

ALWAYS_ALLOWED_ENDPOINTS = []


class JWTBearer(HttpBearer):
    async def authenticate(self, request, token):
        token = token.split(" ")[1] if " " in token else token
        if await sync_to_async(list)(RevokedToken.objects.filter(token=token)):
            raise HttpError(403, "Token has been revoked")

        try:
            payload = decode(
                token, key=settings.SECRET_KEY, algorithms=["HS256"], audience="webook"
            )
        except DecodeError:
            logging.info("Login failed: Invalid token was supplied.")
            raise HttpError(403, "Unauthorized.")
        except ExpiredSignatureError:
            raise HttpError(403, "Token has expired")

        service_account_id = payload.get("sub")
        if service_account_id is None:
            logging.info("Invalid token")
            raise HttpError(403, "Invalid")

        try:
            service_account = await ServiceAccount.objects.aget(pk=service_account_id)
            if not service_account.is_active:
                logging.critical(
                    f"Deactivated user tried to authenticate: {service_account_id}"
                )
                raise HttpError(403, "This user is deactivated.")

            service_account.last_seen = datetime.now(timezone.utc)
            await service_account.asave()

            operation_id = request.resolver_match.url_name

            if operation_id not in ALWAYS_ALLOWED_ENDPOINTS:
                ep = await APIEndpoint.objects.aget(operation_id=operation_id)

                if not ep:
                    logging.info(
                        f"User {service_account_id} tried to access {operation_id} without permission"
                    )
                    raise HttpError(
                        403, "You do not have permission to access this endpoint"
                    )

            return service_account
        except ServiceAccount.DoesNotExist:
            logging.info(f"Invalid user tried to authenticate: {service_account_id}")
            raise HttpError(403, "Invalid token")


def issue_token(service_account):
    return encode(
        payload={
            "iss": "webook",
            "iat": datetime.now(timezone.utc),
            "aud": "webook",
            "sub": service_account.pk,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.JWT_TOKEN_LIFETIME_MINUTES),
        },
        key=settings.SECRET_KEY,
        algorithm="HS256",
    )
