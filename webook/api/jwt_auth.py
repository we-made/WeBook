from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import logging
from typing import List, Union
from ninja.security import HttpBearer
from webook.api.models import ServiceAccount, RevokedToken, APIScope
from django.conf import settings
from jwt import ExpiredSignatureError, decode, DecodeError, encode
from ninja.errors import HttpError
from django.contrib.auth.models import Group

from webook.users.models import User, UserTokenRevocation

ALWAYS_ALLOWED_ENDPOINTS = []


class TokenType(Enum):
    Access = "access"
    Refresh = "refresh"


class IssueeType(Enum):
    ServiceAccount = "service_account"
    User = "user"


@dataclass
class TokenData:
    """
    Dataclass to hold the decoded token data.
    Will raise ValueError if the token is invalid.
    Will check if the token is revoked.
    """

    def __post_init__(self):
        if self.exp < datetime.now(timezone.utc):
            raise ValueError("Token has expired")
        if self.iat > datetime.now(timezone.utc):
            raise ValueError("Token was issued in the future")
        if self.aud != "webook":
            raise ValueError("Invalid audience")

        sub_artifacts = self.sub.split(":")

        if len(sub_artifacts) != 3:
            raise ValueError("Invalid subject")

        if sub_artifacts[0] not in [
            IssueeType.ServiceAccount.value,
            IssueeType.User.value,
        ]:
            raise ValueError("Invalid issuee type")
        self.issuee_type = IssueeType(sub_artifacts[0])

        if not sub_artifacts[1].isnumeric():
            raise ValueError("Invalid subject")
        self.pk = int(sub_artifacts[1])

        if sub_artifacts[2] not in [TokenType.Access.value, TokenType.Refresh.value]:
            raise ValueError("Invalid token type")
        self.token_type = TokenType(sub_artifacts[2])

        if self.issuee_type == IssueeType.User:
            is_revoked = UserTokenRevocation.objects.filter(
                user_id=self.pk, revocation_timestamp__gt=self.iat
            ).exists()

            if is_revoked:
                raise HttpError(403, "Token has been revoked")

        if RevokedToken.objects.filter(token=self.token_value).exists():
            raise HttpError(403, "Token has been revoked")

    token_value: str

    token_type: TokenType
    issuee_type: IssueeType
    pk: int

    iss: str
    iat: datetime
    aud: str
    sub: str
    exp: datetime


def decode_jwt_token(token: str) -> TokenData:
    try:
        token = token.split(" ")[1] if " " in token else token
        d = decode(
            token, key=settings.SECRET_KEY, algorithms=["HS256"], audience="webook"
        )

        if RevokedToken.objects.filter(token=token).exists():
            raise HttpError(403, "Token has been revoked")

        return TokenData(
            token_value=token,
            iss=d.get("iss"),
            iat=datetime.fromtimestamp(d.get("iat"), timezone.utc),
            aud=d.get("aud"),
            sub=d.get("sub"),
            exp=datetime.fromtimestamp(d.get("exp"), timezone.utc),
        )
    except DecodeError:
        logging.info("Login failed: Invalid token was supplied.")
        raise HttpError(403, "Unauthorized.")
    except ExpiredSignatureError:
        raise HttpError(403, "Token has expired")


class JWTBearer(HttpBearer):
    def __init__(self, groups: List[str] = []):
        """
        Initialize the JWTBearer instance.

        args:
            groups: list of groups that are always allowed to access the endpoint that this instance of JWTBearer is attached to.
        """

        self._allowed_groups = []
        if groups:
            for group in groups:
                if not Group.objects.filter(name=group).exists():
                    raise ValueError(f"Group {group} does not exist.")

                self._allowed_groups.append(group)

        super().__init__()

    def authenticate(self, request, token):
        try:
            token_data = decode_jwt_token(token)
        except ValueError as e:
            logging.info(f"Token validation failed: {e}")
            raise HttpError(403, "Unauthorized.")

        if token_data.token_type == TokenType.Refresh:
            logging.info(f"Refresh token was attempted to be used as an access token.")
            raise HttpError(403, "Invalid token.")

        operation_id = request.resolver_match.url_name
        entity: Union[ServiceAccount, User] = None

        if token_data.issuee_type == IssueeType.ServiceAccount:
            service_account_id = token_data.pk
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
                
                entity = service_account
            except ServiceAccount.DoesNotExist:
                logging.info(
                    f"Invalid user tried to authenticate: {service_account_id}"
                )
                raise HttpError(403, "Invalid token")
        elif token_data.issuee_type == IssueeType.User:
            if self._allowed_groups == []:
                raise HttpError(403, "Users can not access this endpoint")

            user_id = token_data.pk
            if user_id is None:
                logging.info("Invalid token")
                raise HttpError(403, "Invalid")

            try:
                user = User.objects.get(pk=user_id)
                if not user.is_active:
                    logging.critical(
                        f"Deactivated user tried to authenticate: {user_id}"
                    )
                    raise HttpError(403, "This user is deactivated.")

                entity = user

            except User.DoesNotExist:
                logging.info(f"Invalid user tried to authenticate: {user_id}")
                raise HttpError(403, "Invalid token")
        else:
            raise HttpError(403, "Invalid token")

        if operation_id in ALWAYS_ALLOWED_ENDPOINTS:
            return entity  # scope check does not apply to always allowed endpoints

        scopes_on_entity = (
            entity.allowed_endpoints.all()
            if hasattr(entity, "allowed_endpoints")
            else entity.endpoint_scopes.all()
        )

        for scope in scopes_on_entity:
            if scope.operation_id == operation_id:
                return entity

        entity_groups = entity.groups.all()
        for group in entity_groups:
            for scope in group.endpoint_scopes.all():
                if scope.operation_id == operation_id:
                    return entity

        raise HttpError(403, "You do not have permission to access this endpoint")


def issue_token(issuee_type: IssueeType, pk: int, token_type=TokenType.Access) -> str:
    if issuee_type == IssueeType.ServiceAccount and token_type == TokenType.Refresh:
        raise ValueError("Service accounts will not be issued refresh tokens.")

    lifetime_delta = (
        timedelta(minutes=settings.JWT_TOKEN_LIFETIME_MINUTES)
        if token_type == TokenType.Access
        else timedelta(days=1)
    )

    return encode(
        payload={
            "iss": "webook",
            "iat": datetime.now(timezone.utc),
            "aud": "webook",
            "sub": f"{issuee_type.value}:{pk}:{token_type.value}",
            "exp": datetime.now(timezone.utc) + lifetime_delta,
        },
        key=settings.SECRET_KEY,
        algorithm="HS256",
    )
