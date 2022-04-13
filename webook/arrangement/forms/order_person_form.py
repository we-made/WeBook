from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceType, Event, Person


class OrderPersonForEventForm(forms.Form):
    event_pk = forms.IntegerField()
    people_ids = forms.CharField()

    def save(self):
        event = Event.objects.get(id=self.cleaned_data["event_pk"])
        people_pks = (self.cleaned_data["people_ids"]).split(",")

        for pk in people_pks:
            event.people.add(pk)

        event.save()