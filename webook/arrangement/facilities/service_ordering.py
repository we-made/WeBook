import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, Optional

from django.conf import settings
from django.contrib.sites.models import Site

from webook.arrangement.facilities.mailing_service import MailMessageFactory
from webook.arrangement.models import (
    Event,
    Service,
    ServiceEmail,
    ServiceOrder,
    ServiceOrderProcessingRequest,
)


class __ROUTINES(Enum):
    NOTIFY_ORDER_PLACED = 0
    NOTIFY_ORDER_CANCELLED = 1
    NOTIFY_LATE_ORDER = 2
    MANUAL_NOTIFY = 3


# Dictates how long a processing request should be considered valid. Expired processing requests will not be usable,
# meaning that the given link sent in the email will no longer be accessible.
_STD_REQUEST_LIFETIME_IN_DAYS = 7

__MAILING_SERVICE = MailMessageFactory()
__MAILING_SERVICE.register_routine(
    __ROUTINES.NOTIFY_ORDER_PLACED, "mailing/service_orders/order_placed.html"
)
__MAILING_SERVICE.register_routine(
    __ROUTINES.NOTIFY_LATE_ORDER,
    "mailing/service_orders/notify_late.html",
)
__MAILING_SERVICE.register_routine(
    __ROUTINES.NOTIFY_ORDER_CANCELLED,
    "mailing/service_orders/notify_order_cancelled.html",
)
__MAILING_SERVICE.register_routine(
    __ROUTINES.MANUAL_NOTIFY, "mailing/service_orders/notify_manual_notified.html"
)


def initialize_service_ordering(service_order: ServiceOrder) -> ServiceOrder:
    """Takes an already established service order and ingests it into the pipeline of service
    ordering logic and process flow, starting with notifying the coordinators responsible for the ordered service
    that there is a new service order awaiting their attention."""

    ordered_service: Service = service_order.service

    for coordinator in ordered_service.emails.all():
        processing_request = ServiceOrderProcessingRequest()
        processing_request.related_to_order = service_order
        processing_request.recipient = coordinator
        processing_request.code = secrets.token_urlsafe(120)
        processing_request.expires_at = datetime.now() + timedelta(
            days=_STD_REQUEST_LIFETIME_IN_DAYS
        )
        processing_request.save()

        __MAILING_SERVICE.send(
            routine_key=__ROUTINES.NOTIFY_ORDER_PLACED,
            subject="Ny tjenestebestilling",
            recipients=[coordinator.email],
            context={"URL_TO_PROCESSING": processing_request.construct_url()},
        )


def send_confirmation_emails():
    pass
