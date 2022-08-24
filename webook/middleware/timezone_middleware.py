# import zoneinfo

import pytz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.pk:
            timezone.activate(pytz.timezone(request.user.timezone))
        else:
            timezone.deactivate()

        return self.get_response(request)
