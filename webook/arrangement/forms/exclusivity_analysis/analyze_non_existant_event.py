from django import forms
from numpy import require

from webook.arrangement.models import Arrangement, Event


class AnalyzeNonExistantEvent(forms.Form):
    title = forms.CharField(max_length=255)
    title_en = forms.CharField(max_length=255)
    ticket_code = forms.CharField(max_length=255)
    expected_visitors = forms.IntegerField(required=False)
    fromDate = forms.DateField()
    fromTime = forms.TimeField()
    toDate = forms.DateField()
    toTime = forms.TimeField()

    display_layouts = forms.CharField(max_length=1024, required=False)
    rooms = forms.CharField(max_length=1024, required=False)
    people = forms.CharField(max_length=1024, required=False)

    def as_dict(self):
        event = {
            "title": self.cleaned_data["title"],
            "title_en": self.cleaned_data["title_en"],
            "ticket_code": self.cleaned_data["ticket_code"],
            "expected_visitors": self.cleaned_data["expected_visitors"],
            "fromDate": self.cleaned_data["fromDate"],
            "fromTime": self.cleaned_data["fromTime"],
            "toDate": self.cleaned_data["toDate"],
            "toTime": self.cleaned_data["toTime"],
            "display_layouts": [int(display_layout) for display_layout in self.cleaned_data["display_layouts"].split(",") if display_layout],
            "rooms": [int(room) for room in self.cleaned_data["rooms"].split(",") if room],
            "people": [int(person) for person in self.cleaned_data["people"].split(",") if person],
        }
        
        return event
