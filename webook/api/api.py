from django.conf import settings
from ninja import NinjaAPI, Swagger

from webook.api.jwt_auth import JWTBearer
from webook.api.session_auth import AuthAgent
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from webook.api.routers.service_account_router import service_account_router
from ninja.security import django_auth

api = NinjaAPI(
    title="WeBook V1 API",
    docs=Swagger() if settings.DEBUG else None,
    description="WeBook API",
    auth=[django_auth, JWTBearer()],
    openapi_extra={"tags": []},
)
api.add_router("/service_accounts", service_account_router)


@api.exception_handler(ObjectDoesNotExist)
def handle_does_not_exist(request, exc):
    return api.create_response(request, {"error": "Not Found"}, status=404)


@api.exception_handler(PermissionDenied)
def handle_permission_denied(request, exc):
    return api.create_response(request, {"error": "Permission Denied"}, status=403)


@api.exception_handler(Exception)
def handle_exception(request, exc):
    if settings.DEBUG:
        raise exc

    if hasattr(exc, "message"):
        return api.create_response(request, {"error": exc.message}, status=500)

    return api.create_response(request, {"error": "Internal Server Error"}, status=500)
