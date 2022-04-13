from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceType, Event, Room

class OrderRoomForSerieForm (forms.Form):
    serie_guid = forms.UUIDField()
    room_ids = forms.CharField()

    def is_guid_known():
        pass

    def save(self):
        serie_sequence_guid = self.cleaned_data["serie_guid"]
        room_ids_arr = (self.cleaned_data["room_ids"]).split(",")

        events_in_serie = Event.objects.filter(sequence_guid=serie_sequence_guid)

        for event in events_in_serie:
            for room_id in room_ids_arr:
                event.rooms.add(room_id)
            event.save()