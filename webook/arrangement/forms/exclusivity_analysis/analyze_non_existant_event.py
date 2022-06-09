from django import forms

from webook.arrangement.dto.event import EventDTO
from webook.arrangement.models import Arrangement, Event


class AnalyzeNonExistantEventForm(forms.Form):
    title = forms.CharField(max_length=255)
    title_en = forms.CharField(max_length=255)
    ticket_code = forms.CharField(max_length=255, required=False)
    expected_visitors = forms.IntegerField(required=False)
    fromDate = forms.DateTimeField()
    toDate = forms.DateTimeField()
    display_layouts = forms.CharField(max_length=1024, required=False)
    rooms = forms.CharField(max_length=1024, required=False)
    people = forms.CharField(max_length=1024, required=False)

    def as_dict(self):
        event = {
            "title": self.cleaned_data["title"],
            "title_en": self.cleaned_data["title_en"],
            "ticket_code": self.cleaned_data["ticket_code"],
            "expected_visitors": self.cleaned_data["expected_visitors"],
            "start": self.cleaned_data["fromDate"],
            "end": self.cleaned_data["toDate"],
            "fromDate": self.cleaned_data["fromDate"].date,
            "fromTime": self.cleaned_data["fromDate"].time,
            "toDate": self.cleaned_data["toDate"].date,
            "toTime": self.cleaned_data["toDate"].time,
            "display_layouts": [int(display_layout) for display_layout in self.cleaned_data["display_layouts"].split(",") if display_layout],
            "rooms": [int(room) for room in self.cleaned_data["rooms"].split(",") if room],
            "people": [int(person) for person in self.cleaned_data["people"].split(",") if person],
        }
        
        return event

    def as_event_dto(self):
        event = EventDTO(
            title=self.cleaned_data["title"],
            title_en=self.cleaned_data["title_en"],
            start=self.cleaned_data["fromDate"],
            end=self.cleaned_data["toDate"],
            rooms=[int(room) for room in self.cleaned_data["rooms"].split(",") if room]
        )
        return event
