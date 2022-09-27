from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from webook.arrangement.models import Arrangement, RoomPreset


class PlannerCreateArrangementModelForm(forms.ModelForm):

    display_text = forms.CharField(required=False)
    display_text_en = forms.CharField(required=False)

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
                    "meeting_place_en",
                    "expected_visitors",
                    "display_layouts",
                    "status",
                    "display_text",
                    "display_text_en",)
        widgets = { "display_layouts": CheckboxSelectMultiple(),
                    "location": forms.Select(attrs={"class": "form-control form-control-md", "data-mdb-validation": "true"}),
                    "audience": forms.Select(attrs={"class": "form-control", "data-mdb-placeholder": "Select audience", "data-mdb-validation": "true"}),
                    "arrangement_type": forms.Select(attrs={"class": "form-control-md", "data-mdb-validation": "true"}),
                    "responsible": forms.Select(attrs={"class": "form-control-md", "data-mdb-validation": "true"}), 
                    "status": forms.Select(attrs={"class": "form-control"})}
