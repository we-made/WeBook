from django import forms
from webook.arrangement.models import Arrangement, Person, Event


class RemovePersonFromEventForm (forms.Form):
    event_pk = forms.IntegerField()
    person_pk = forms.IntegerField()

    def remove(self):
        cleaned_event_pk = self.cleaned_data["event_pk"]
        cleaned_person_pk = self.cleaned_data["person_pk"]

        event = Event.objects.get(id=cleaned_event_pk)
        event.people.remove(cleaned_person_pk)