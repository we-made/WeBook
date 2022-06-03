from django import forms
from webook.arrangement.models import Arrangement, RoomPreset
from django.forms.widgets import CheckboxSelectMultiple


class PlannerCreateArrangementModelForm(forms.ModelForm):
    class Meta:
        model = Arrangement
        fields = (  "name",
                    "name_en",
                    "audience",
                    "arrangement_type",
                    "location",
                    "responsible",
                    "ticket_code",
                    "meeting_place",
                    "expected_visitors",
                    "display_layouts",
                    "display_text",
                    "display_text_en",)
        widgets = { "display_layouts": CheckboxSelectMultiple(), }
