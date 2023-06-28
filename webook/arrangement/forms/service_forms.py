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
    EventSerie,
    Person,
    Service,
    ServiceEmail,
    ServiceOrder,
    ServiceOrderInternalChangelog,
    ServiceOrderPreconfiguration,
    ServiceOrderProcessingRequest,
    ServiceOrderProvision,
    States,
)
from webook.users.models import User


class AddEmailForm(forms.Form):
    service_id = forms.IntegerField()
    email = forms.EmailField()

    def save(self):
        service_id = self.cleaned_data["service_id"]
        email = self.cleaned_data["email"]

        service = Service.objects.get(id=service_id)

        if service.emails.filter(email=email).exists():
            return "Email already exists"

        service.add_email(ServiceEmail(email=email))
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
        fields = [
            "id",
            "selected_personell",
            "is_complete",
            "freetext_comment",
            "comment_to_personell",
        ]
        widgets = {
            "selected_personell": TableSimpleMultiSelectWidget,
            "freetext_comment": Textarea(attrs={"class": "form-control"}),
        }


class AddPersonToPreconfigurationForm(forms.ModelForm):
    class Meta:
        model = ServiceOrderPreconfiguration
        fields = ["id", "assigned_personell"]
        widgets = {"personell": TableMultiSelectWidget()}


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

        # Get all SOPR related to this email
        issued_soprs = ServiceOrderProcessingRequest.objects.filter(recipient=email)

        for sopr in issued_soprs:
            sopr.delete()


class CancelServiceOrderForm(forms.Form):
    service_order_id = forms.IntegerField()

    def save(self):
        service_order_id = self.cleaned_data["service_order_id"]
        service_order = ServiceOrder.objects.get(id=service_order_id)
        ordering_service.cancel_service_order(service_order)


class OpenServiceOrderForRevisioningForm(forms.Form):
    service_order_id = forms.IntegerField()

    def save(self):
        service_order_id = self.cleaned_data["service_order_id"]
        service_order = ServiceOrder.objects.get(id=service_order_id)
        ordering_service.open_service_order_for_revisioning(service_order)


class OrderServiceForm(forms.Form):
    parent_type = forms.ChoiceField(
        choices=(("serie", "Serie"), ("event", "Event"), ("unknown", "Unknown"))
    )
    parent_id = forms.IntegerField()
    service_id = forms.IntegerField()
    applied_preconfiguration = forms.ModelChoiceField(
        queryset=ServiceOrderPreconfiguration.objects.all(), required=False
    )
    freetext_comment = forms.CharField(max_length=5024, required=False)

    service_order = forms.ModelChoiceField(
        queryset=ServiceOrder.objects.all(), required=False
    )

    def save(self, user: User):
        parent_id = self.cleaned_data["parent_id"]
        service_id = self.cleaned_data["service_id"]
        freetext_comment = self.cleaned_data["freetext_comment"]
        parent_type = self.cleaned_data["parent_type"]
        service_order: Optional[ServiceOrder] = self.cleaned_data["service_order"]
        applied_preconfiguration = self.cleaned_data["applied_preconfiguration"]

        service = Service.objects.get(
            id=service_id
        )  # We should rewrite to use ModelChoiceField instead of id - this is stupid, I've likely done this before all over the place

        if applied_preconfiguration and applied_preconfiguration.service != service:
            raise ValueError("Preconfiguration does not match service")

        is_new = service_order is None

        if is_new:
            service_order = ServiceOrder()
            service_order.service = service
            service_order.applied_preconfiguration = applied_preconfiguration
            service_order.freetext_comment = freetext_comment
            service_order.state = States.AWAITING
            service_order.save()

        if parent_type == "serie":
            serie = EventSerie.objects.get(id=parent_id)
            service_order.events.add(*serie.events.all())
            serie.serie_plan_manifest.orders.add(service_order)
        if parent_type == "event":
            event = Event.objects.get(id=parent_id)
            service_order.events.add(event)

        if user and user.person:
            service_order.created_by = user.person

        service_order.save()

        if is_new:
            ordering_service.initialize_service_ordering(service_order)
        else:
            ordering_service.reinitialize_service_ordering(service_order)


class UpdateServiceOrderForm(forms.Form):
    class Meta:
        model = ServiceOrder
        fields = "freetext_comment"


class RegisterServiceTemplate(forms.ModelForm):
    def save():
        pass


class CreateNoteView(forms.ModelForm):
    class Meta:
        model = ServiceOrderInternalChangelog
        fields = ("source_sopr", "service_order", "changelog_message")
