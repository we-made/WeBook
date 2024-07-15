from datetime import datetime, timedelta, timezone
import logging
from ninja.security import HttpBearer
from webook.api.models import ServiceAccount, RevokedToken
from django.conf import settings
from jwt import ExpiredSignatureError, decode, DecodeError, encode
from ninja.errors import HttpError


class JWTBearer(HttpBearer):
    def authenticate(self, request, token):
        token = token.split(" ")[1]
        if RevokedToken.objects.filter(token=token).exists():
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
            service_account = ServiceAccount.objects.get(pk=service_account_id)
            if not service_account.is_active:
                logging.critical(
                    f"Deactivated user tried to authenticate: {service_account_id}"
                )
                raise HttpError(403, "This user is deactivated.")

            service_account.last_seen = datetime.now(timezone.utc)
            service_account.save()

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
