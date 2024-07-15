from django.conf import settings
from ninja import NinjaAPI, Swagger

from webook.api.session_auth import AuthAgent
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

api = NinjaAPI(
    title="WeBook V1 API",
    docs=Swagger() if settings.DEBUG else None,
    description="WeBook API",
    auth=AuthAgent(
        authorize_hook=lambda user: True
    ),  # Will only pass if user is authenticated, which we want.
    openapi_extra={"tags": []},
)
# Allows setting the description of a tag - not supported by NinjaAPI out of the box on the tag declaration itself.
api.set_tag_doc = lambda tag, doc: api.openapi_extra["tags"].append(
    {"name": tag, "description": doc}
)


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
