from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from webook.arrangement.models import Arrangement, RoomPreset


class PlannerUpdateArrangementModelForm(forms.ModelForm):
    class Meta:
        model = Arrangement
        fields = (  "name",
                    "name_en",
                    "audience",
                    "arrangement_type",
                    "location",
                    "ticket_code",
                    "meeting_place",
                    "meeting_place_en",
                    "expected_visitors",
                    "actual_visitors",
                    "display_layouts",
                    "status",)
        widgets = { "display_layouts": CheckboxSelectMultiple(), "location": forms.Select(attrs={"class": "form-control form-control-lg"}) }
