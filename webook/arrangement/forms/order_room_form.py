from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceType, Event, Person


class OrderRoomForEventForm(forms.Form):
    event_pk = forms.IntegerField()
    room_ids = forms.CharField()

    def save(self):
        event = Event.objects.get(id=self.cleaned_data["event_pk"])
        room_pks = (self.cleaned_data["room_ids"]).split(",")

        for pk in room_pks:
            event.rooms.add(pk)

        event.save()