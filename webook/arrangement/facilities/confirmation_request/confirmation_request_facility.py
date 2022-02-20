from re import template
import string
from webook.arrangement.models import ConfirmationReceipt, Person
from enum import Enum
from django.core.mail import send_mail, EmailMessage
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
import secrets
import uuid
from django.core.exceptions import ObjectDoesNotExist


_FAIL_SILENTLY=False

class InvalidRequestCodeException(Exception):
    """ Raised when an invalid request code is supplied """
    # TODO: Consider the need of logging invalid code redemptions. This is the best place to do so.
    pass


class MailMessageFactory():
    class ROUTINES(Enum):
        NOTIFY_REQUEST_MADE=1
        NOTIFY_REQUEST_CANCELLED=2
        NOTIFY_REQUEST_CONFIRMED=3
        NOTIFY_REQUEST_DENIED=4

    class BaseContextFabricator():
        def fabricate(confirmation_receipt):
            return {
                "ORIGINATOR_FRIENDLY_NAME": "The Real WeBook",
                "recipient": "magnus@wemade.no"
            }

    def fabricate_email_message(self, routine: ROUTINES, confirmation_receipt: ConfirmationReceipt):
        mail_message = EmailMessage()
        fabrication_routine_options_dict = self._get_fabrication_strategy_map()[routine]
        
        mail_message.to = [confirmation_receipt.sent_to]
        mail_message.subject = fabrication_routine_options_dict["subject"]
        mail_message.body = self._generate_mailbody_from_template(
            template=fabrication_routine_options_dict["template"],
            context=fabrication_routine_options_dict["context_builder"]()
        )

        return mail_message

    def _get_fabrication_strategy_map(self):
        """ 
            Get the fabrication strategy map, providing routine-specific information necessary
            for tailored fabrications
        """
        return {
            self.ROUTINES.NOTIFY_REQUEST_MADE: { 
                "template": "mailing/confirmation_request/notify_request_made.html",
                "subject": _("Request of confirmation"),
                "context_builder": self.BaseContextFabricator().fabricate,
                },
            self.ROUTINES.NOTIFY_REQUEST_CANCELLED: {
                "template": "mailing/confirmation_request/notify_request_cancelled.html",
                "subject": _("Request cancelled"),
                "context_builder": self.BaseContextFabricator().fabricate,
            },
            self.ROUTINES.NOTIFY_REQUEST_DENIED: {
                "template": "mailing/confirmation_request/request_denied_receipt.html",
                "subject": _("Request denial receipt"),
                "context_builder": self.BaseContextFabricator().fabricate,
            },
            self.ROUTINES.NOTIFY_REQUEST_CONFIRMED: {
                "template": "mailing/confirmation_request/request_confirmed_receipt.html",
                "subject": _("Request confirmation receipt"),
                "context_builder": self.BaseContextFabricator().fabricate,
            },
        }

    def _generate_mailbody_from_template(self, template, context):
        """ 
            Generate the body of the mail using the given template
        """
        return render_to_string(template, context)


def _validate_request_obj(request:ConfirmationReceipt):
    if (request is None):
        raise InvalidRequestCodeException()

def is_request_token_valid(token:str):
    if not token: 
        return False

    try: 
        if ConfirmationReceipt.objects.get(code=token) is None: 
            return False
    except ObjectDoesNotExist:
        return False

    return True


def make_request (recipient_email: str, requested_by: Person):
    """
        Make a new confirmation request
    """
    request = ConfirmationReceipt()
    request.code = secrets.token_urlsafe(120)
    request.sent_to = recipient_email
    request.requested_by = requested_by

    request.save()

    email_message = MailMessageFactory().fabricate_email_message(
        routine=MailMessageFactory.ROUTINES.NOTIFY_REQUEST_MADE,
        confirmation_receipt=request,
    )

    return bool(email_message.send(fail_silently=_FAIL_SILENTLY))


def cancel_request(code:str):
    """
        Cancel a confirmation request
    """
    request = ConfirmationReceipt.objects.get(code=code)
    _validate_request_obj(request)

    request.state = ConfirmationReceipt.CANCELLED
    request.save()

    email_message = MailMessageFactory().fabricate_email_message(
        routine=MailMessageFactory.ROUTINES.NOTIFY_REQUEST_CANCELLED,
        confirmation_receipt=request
    )
    return bool(email_message.send(fail_silently=_FAIL_SILENTLY))


def deny_request(code:str, denial_reason:str=None):
    """ 
        Deny a confirmation request
    """
    request = ConfirmationReceipt.objects.get(code=code)
    _validate_request_obj(request)

    request.state = ConfirmationReceipt.DENIED
    if (denial_reason):
        request.denial_reasoning = denial_reason
    request.save()

    email_message = MailMessageFactory().fabricate_email_message(
        routine=MailMessageFactory.ROUTINES.NOTIFY_REQUEST_DENIED,
        confirmation_receipt=request
    )
    return bool(email_message.send(fail_silently=_FAIL_SILENTLY))


def confirm_request(code:str):
    """
        Confirm a confirmation request
    """
    request = ConfirmationReceipt.objects.get(code=code)
    _validate_request_obj(request)

    request.state = ConfirmationReceipt.CONFIRMED
    request.save()

    email_message = MailMessageFactory().fabricate_email_message(
        routine=MailMessageFactory.ROUTINES.NOTIFY_REQUEST_CONFIRMED,
        confirmation_receipt=request
    )
    return bool(email_message.send(fail_silently=_FAIL_SILENTLY))