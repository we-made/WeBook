from django.conf import settings
from ninja import NinjaAPI, Swagger

from webook.api.jwt_auth import JWTBearer
from webook.api.session_auth import AuthAgent
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from webook.api.routers.service_account_router import service_account_router
from ninja.security import django_auth
from webook.arrangement.api import audience_router

from webook.onlinebooking.api import (
    county_router,
    city_segment_router,
    school_router,
    online_booking_router,
)

api = NinjaAPI(
    title="WeBook V1 API",
    docs=Swagger() if settings.DEBUG else None,
    description="WeBook API",
    # JWTBearer() needs to be the first to be attempted
    # If django_auth goes first, CSRF will be checked. This messes up if you're using the onlinebooking
    # app.
    auth=[JWTBearer(), django_auth], 
    openapi_extra={"tags": []},
)
api.add_router("/service_accounts", service_account_router)
api.add_router("/onlinebooking/county", county_router)
api.add_router("/onlinebooking/city_segment", city_segment_router)
api.add_router("/onlinebooking/school", school_router)
api.add_router("/onlinebooking/online_booking", online_booking_router)
api.add_router("/arrangement/audience", audience_router)


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
