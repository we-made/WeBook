from django import forms
from webook.arrangement.models import Arrangement, Person, Event, Room


class RemoveRoomFromEventForm (forms.Form):
    event_pk = forms.IntegerField()
    room_pk = forms.IntegerField()

    def remove(self):
        cleaned_event_pk = self.cleaned_data["event_pk"]
        cleaned_room_pk = self.cleaned_data["room_pk"]

        event = Event.objects.get(id=cleaned_event_pk)
        event.rooms.remove(cleaned_room_pk)