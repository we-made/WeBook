import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, Optional, Union

from django.conf import settings
from django.contrib.sites.models import Site

from webook.arrangement.facilities.mailing_service import MailMessageFactory
from webook.arrangement.models import (
    Event,
    Service,
    ServiceEmail,
    ServiceOrder,
    ServiceOrderProcessingRequest,
    ServiceOrderProvision,
    States,
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


class InvalidProcessingRequestTokenException(Exception):
    """Exception raised when a given token for a Service Order Processing Request is invalid/not known."""

    pass


class ServiceOrderIsFinalException(Exception):
    """Exception raised when trying to affect the state of a Service Order that is final"""

    pass


def _assert_affectable(service_order: ServiceOrder) -> ServiceOrder:
    """Helper method for asserting if a ServiceOrder is affectable (not final), raising an exception if yes, returning the
    ServiceOrder if not

    Arguments:
        service_order: The service order to sanity check

    Raises:
        ServiceOrderIsFinalException: Raised if the given Service Order is final, and can not legally be affected further
    """
    if service_order.is_final:
        raise ServiceOrderIsFinalException()

    return service_order


def _resolve_service_order(
    service_order_or_token: Union[ServiceOrder, str]
) -> ServiceOrder:
    """Internal helper function to centralize the handling of the ambigous service_order_or_token
    parameter that repeats on some functions. In practice this function resolves the given parameter,
    condensing it down to a guaranteed ServiceOrder.
    The token must be a valid reference to a processing request.

    Arguments:
        service_order_or_token: Either a ServiceOrder instance, or a string token. The token must refer to a valid processing request.
    """
    if isinstance(service_order_or_token, str):
        # Get the processing request associated with the given token
        processing_request = ServiceOrderProcessingRequest.objects.get(
            code=service_order_or_token
        )
        if processing_request is None:
            raise Exception("Invalid token")

        return processing_request.related_to_order
    elif not isinstance(service_order_or_token, ServiceOrder):
        raise Exception("Not a valid service order")
    else:
        return service_order_or_token


def confirm_service_order(service_order_or_token: Union[ServiceOrder, str]) -> None:
    """Confirm a given service order, moving it into the final CONFIRMED state"""
    service_order: ServiceOrder = _assert_affectable(
        _resolve_service_order(service_order_or_token)
    )

    provisions = service_order.provisions.all()

    if not all(map(lambda provision: provision.is_complete, provisions)):
        raise Exception("All activities have yet to be provisioned")

    service_order.state = States.CONFIRMED
    service_order.save()


def cancel_service_order(service_order: ServiceOrder) -> None:
    """Cancel a given service order, moving it into the final CANCELLED state
    We don't allow service-order-by-token here because the coordinators can not cancel a request.
    Only the planners (those who place the request) can cancel it.

    Arguments:
        service_order: The service order that which is to be cancelled
    """

    _: ServiceOrder = _assert_affectable(service_order)

    service_order.state = States.CANCELLED
    service_order.save()


def deny_service_order(service_order_or_token: Union[ServiceOrder, str]) -> None:
    """Deny a given service order, moving it into the final DENY state

    Arguments:
        service_order_or_token: Either a ServiceOrder instance, or a valid token for a processing request associated with a
                                ServiceOrder. Designates the ServiceOrder that which is to be denied.

    Raises:
        Exception: If token is invalid (not associated with any known processing requests) or the given instance is not a ServiceOrder
    """
    service_order: ServiceOrder = _assert_affectable(
        _resolve_service_order(service_order_or_token)
    )

    service_order.state = States.DENIED
    service_order.save()


def initialize_service_ordering(service_order: ServiceOrder) -> ServiceOrder:
    """Takes an already established service order and ingests it into the pipeline of service
    ordering logic and process flow, starting with notifying the coordinators responsible for the ordered service
    that there is a new service order awaiting their attention."""

    ordered_service: Service = service_order.service

    for event in service_order.events.all():
        provision = ServiceOrderProvision(
            related_to_order=service_order,
            for_event=event,
            sopr_resolving_this=None,
        )
        provision.save()

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
            context={
                "URL_TO_PROCESSING": processing_request.construct_url(),
                "PLANNER_FREETEXT": processing_request.related_to_order.freetext_comment,
                "SERVICE_NAME": processing_request.related_to_order.service.name,
            },
            is_html=True,
        )


def send_confirmation_emails():
    pass
