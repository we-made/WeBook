from typing import Optional, Tuple

from django import forms

from webook.arrangement.facilities import service_ordering as ordering_service
from webook.arrangement.forms.widgets.table_multi_select import TableMultiSelectWidget
from webook.arrangement.models import (
    Event,
    Person,
    Service,
    ServiceEmail,
    ServiceOrder,
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


class AddPersonForm(forms.ModelForm):
    # resources = forms.ModelMultipleChoiceField(
    #     queryset=Person.objects, widget=TableMultiSelectWidget
    # )
    class Meta:
        model = Service
        fields = ["id", "resources"]
        widgets = {"resources": TableMultiSelectWidget()}


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
