import requests
import jwt
from webook.api.models import ServiceAccount
from django.db.models import Q

from webook import logger

GOOGLE_ISSUER = "https://accounts.google.com"
GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"


def fetch_google_public_keys():
    response = requests.get(GOOGLE_CERTS_URL)
    response.raise_for_status()
    return response.json()


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
            issuer=GOOGLE_ISSUER
        )

        email = decoded_token.get("email")

        if not email:
            raise Exception("Invalid email")
    
        service_account = ServiceAccount.objects.filter(
            Q(email=email) & Q(service_account_type=ServiceAccount.GOOGLE_SERVICE_ACCOUNT)
        ).first()

        if not service_account:
            raise Exception("Service account not found")

        return service_account
    except Exception as e:
        print("Token verification failed." + str(e))
        logger.exception(e)
        return None
