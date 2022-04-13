from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceType, Event, Person

class OrderPersonForSerieForm (forms.Form):
    serie_guid = forms.UUIDField()
    people_ids = forms.CharField()

    def is_guid_known():
        pass

    def save(self):
        serie_sequence_guid = self.cleaned_data["serie_guid"]
        person_ids_arr = (self.cleaned_data["people_ids"]).split(",")

        events_in_serie = Event.objects.filter(sequence_guid=serie_sequence_guid)

        for event in events_in_serie:
            for person_id in person_ids_arr:
                event.people.add(person_id)
            event.save()