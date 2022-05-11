from django import forms
from webook.arrangement.models import Arrangement, RoomPreset, Event
from django.forms.widgets import CheckboxSelectMultiple


class PlannerUpdateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (          
            "title",
            "title_en",
            "start",
            "end",
            "ticket_code",
            "expected_visitors",
            "actual_visitors",
            "display_layouts",)
        widgets = { "display_layouts": CheckboxSelectMultiple(), }