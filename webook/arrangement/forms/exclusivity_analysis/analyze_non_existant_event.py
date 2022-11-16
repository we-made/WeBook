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

    before_buffer_title = forms.CharField(required=False, max_length=512)
    before_buffer_date = forms.DateField(
        required=False,
    )
    before_buffer_date_offset = forms.IntegerField(
        required=False,
    )
    before_buffer_start = forms.TimeField(
        required=False,
    )
    before_buffer_end = forms.TimeField(
        required=False,
    )

    after_buffer_title = forms.CharField(required=False, max_length=512)
    after_buffer_date = forms.DateField(
        required=False,
    )
    after_buffer_date_offset = forms.IntegerField(
        required=False,
    )
    after_buffer_start = forms.TimeField(
        required=False,
    )
    after_buffer_end = forms.TimeField(
        required=False,
    )

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
            "after_buffer_title": self.cleaned_data["after_buffer_title"],
            "after_buffer_date": self.cleaned_data["after_buffer_date"],
            "after_buffer_date_offset": self.cleaned_data["after_buffer_date_offset"],
            "after_buffer_start": self.cleaned_data["after_buffer_start"],
            "after_buffer_end": self.cleaned_data["after_buffer_end"],
            "before_buffer_title": self.cleaned_data["before_buffer_title"],
            "before_buffer_date": self.cleaned_data["before_buffer_date"],
            "before_buffer_date_offset": self.cleaned_data["before_buffer_date_offset"],
            "before_buffer_start": self.cleaned_data["before_buffer_start"],
            "before_buffer_end": self.cleaned_data["before_buffer_end"],
            "display_layouts": [
                int(display_layout)
                for display_layout in self.cleaned_data["display_layouts"].split(",")
                if display_layout
            ],
            "rooms": [
                int(room) for room in self.cleaned_data["rooms"].split(",") if room
            ],
            "people": [
                int(person)
                for person in self.cleaned_data["people"].split(",")
                if person
            ],
        }

        return event

    def as_event_dto(self):
        event = EventDTO(
            title=self.cleaned_data["title"],
            title_en=self.cleaned_data["title_en"],
            after_buffer_title=self.cleaned_data["after_buffer_title"],
            after_buffer_date=self.cleaned_data["after_buffer_date"],
            after_buffer_date_offset=self.cleaned_data["after_buffer_date_offset"],
            after_buffer_start=self.cleaned_data["after_buffer_start"],
            after_buffer_end=self.cleaned_data["after_buffer_end"],
            before_buffer_title=self.cleaned_data["before_buffer_title"],
            before_buffer_date=self.cleaned_data["before_buffer_date"],
            before_buffer_date_offset=self.cleaned_data["before_buffer_date_offset"],
            before_buffer_start=self.cleaned_data["before_buffer_start"],
            before_buffer_end=self.cleaned_data["before_buffer_end"],
            start=self.cleaned_data["fromDate"],
            end=self.cleaned_data["toDate"],
            rooms=[int(room) for room in self.cleaned_data["rooms"].split(",") if room],
        )
        return event
