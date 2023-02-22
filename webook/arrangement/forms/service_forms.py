from typing import List, Optional, Tuple

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.widgets import Textarea

from webook.arrangement.facilities import service_ordering as ordering_service
from webook.arrangement.forms.widgets.table_multi_select import (
    TableMultiSelectWidget,
    TableSimpleMultiSelectWidget,
)
from webook.arrangement.models import (
    Event,
    Person,
    Service,
    ServiceEmail,
    ServiceOrder,
    ServiceOrderProcessingRequest,
    ServiceOrderProvision,
    States,
)


class AddEmailForm(forms.Form):
    service_id = forms.IntegerField()
    email = forms.EmailField()

    def save(self):
        service_id = self.cleaned_data["service_id"]
        email = self.cleaned_data["email"]

        service = Service.objects.get(id=service_id)

        if service.emails.filter(email=email).exists():
            raise Exception("Email already exists")

        new_service_email = ServiceEmail(email=email)
        new_service_email.save()
        service.emails.add(new_service_email)
        service.save()


def sopr_token_validator(value):
    """Validate the given token"""
    sopr = ServiceOrderProcessingRequest.objects.get(code=value)
    if sopr is None:
        raise forms.ValidationError("Invalid token/code supplied")


class ProvisionPersonellForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        self.base_fields["selected_personell"].queryset = kwargs.pop("personell_qs")
        super().__init__(*args, **kwargs)

    class Meta:
        model = ServiceOrderProvision
        fields = ["id", "selected_personell", "is_complete", "freetext_comment"]
        widgets = {
            "selected_personell": TableSimpleMultiSelectWidget,
            "freetext_comment": Textarea(attrs={"class": "form-control"}),
        }


class AddPersonForm(forms.ModelForm):
    # resources = forms.ModelMultipleChoiceField(
    #     queryset=Person.objects, widget=TableMultiSelectWidget
    # )
    class Meta:
        model = Service
        fields = ["id", "resources"]
        widgets = {"resources": TableMultiSelectWidget()}


class DenyServiceOrderForm(forms.Form):
    token = forms.CharField(max_length=1024)

    def save(self):
        token = self.cleaned_data["token"]

        sopr: Optional[
            ServiceOrderProcessingRequest
        ] = ServiceOrderProcessingRequest.objects.get(code=token)

        if sopr is None:
            raise ObjectDoesNotExist()

        ordering_service.deny_service_order(sopr.related_to_order)


class ConfirmServiceOrderForm(forms.Form):
    token = forms.CharField(max_length=1024)

    def save(self):
        token = self.cleaned_data["token"]

        sopr: Optional[
            ServiceOrderProcessingRequest
        ] = ServiceOrderProcessingRequest.objects.get(code=token)

        if sopr is None:
            raise ObjectDoesNotExist()

        ordering_service.confirm_service_order(sopr.related_to_order)


class DeleteEmailForm(forms.Form):
    """Form for deleting an email from a service"""

    service_id = forms.IntegerField()
    email = forms.EmailField()

    def save(self):
        service_id = self.cleaned_data["service_id"]
        email = self.cleaned_data["email"]

        service = Service.objects.get(id=service_id)
        email_instance = service.emails.filter(email=email)

        if email_instance:
            email_instance.delete()


class OrderServiceForActivityForm(forms.Form):
    event_id = forms.IntegerField()
    service_id = forms.IntegerField()
    freetext_comment = forms.CharField(max_length=5024)

    def save(self):
        service_id = self.cleaned_data["service_id"]
        event_id = self.cleaned_data["event_id"]
        freetext_comment = self.cleaned_data["freetext_comment"]

        service = Service.objects.get(id=service_id)
        event = Event.objects.get(id=event_id)

        service_order = ServiceOrder()
        service_order.service = service
        service_order.freetext_comment = freetext_comment
        service_order.state = States.AWAITING

        service_order.save()

        service_order.events.add(event)

        service_order.save()

        ordering_service.initialize_service_ordering(service_order)


class UpdateServiceOrderForm(forms.Form):
    class Meta:
        model = ServiceOrder
        fields = "freetext_comment"


class RegisterServiceTemplate(forms.ModelForm):
    def save():
        pass
