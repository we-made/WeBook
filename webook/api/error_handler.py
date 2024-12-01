import json
from django.http import HttpResponse
from ninja import NinjaAPI
from ninja.errors import HttpError


class TranslatedHttpError(HttpError):
    def __init__(self, status_code: int, message: str, message_no: str):
        super().__init__(status_code, message=message)
        self.message_no = message_no


def bad_request_error_handler(request, exc):
    return HttpResponse(
        status=400,
        content=json.dumps(
            {
                "message": exc.message,
                "message_no": exc.message_no,
            }
        ),
    )


def register_handlers(api: NinjaAPI):
    api.add_exception_handler(TranslatedHttpError, bad_request_error_handler)
