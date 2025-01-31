import json
import requests
import jwt
from webook.api.models import ServiceAccount
from django.db.models import Q
from ninja.security import HttpBearer
from ninja.errors import HttpError
from jwt.algorithms import RSAAlgorithm
from webook import logger

GOOGLE_ISSUER = "https://accounts.google.com"
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"


def fetch_google_public_keys():
    response = requests.get(GOOGLE_CERTS_URL)
    keys = response.json().get("keys", [])
    return {key["kid"]: RSAAlgorithm.from_jwk(json.dumps(key)) for key in keys}


def verify_google_jwt(token: str, audience: str):
    try:
        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header.get("kid")

        keys = fetch_google_public_keys()

        if key_id not in keys:
            raise Exception("Invalid key id")

        decoded_token = jwt.decode(
            token,
            keys[key_id],
            algorithms=["RS256"],
            audience=audience,
            issuer=GOOGLE_ISSUER,
            verify=True,
        )

        email = decoded_token.get("email")

        if not email:
            raise Exception("Invalid email")

        service_account = ServiceAccount.objects.filter(
            Q(email=email)
            & Q(service_account_type=ServiceAccount.GOOGLE_SERVICE_ACCOUNT)
        ).first()

        if not service_account:
            raise Exception("Service account not found")

        return service_account
    except Exception as e:
        print("Token verification failed." + str(e))
        return None


class GoogleOidcBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            service_account = verify_google_jwt(token, "webook")
        except Exception as e:
            return None
            # raise HttpError(403, "Unauthorized.")

        if not service_account:
            return None
            # raise HttpError(403, "Unauthorized.")

        return service_account
