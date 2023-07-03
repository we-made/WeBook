from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from webook.arrangement.models import Arrangement, Person, RoomPreset


class PlannerCreateArrangementModelForm(forms.ModelForm):
    display_text = forms.CharField(required=False)
    display_text_en = forms.CharField(required=False)
    responsible = forms.ModelChoiceField(queryset=Person.objects.all(), required=False)

    class Meta:
        model = Arrangement
        fields = (
            "name",
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
            "planners",
        )
        widgets = {
            "display_layouts": CheckboxSelectMultiple(
                attrs={"v-model": "arrangement.display_layouts"}
            ),
            "display_text": forms.TextInput(
                attrs={"v-model": "arrangement.display_text"}
            ),
            "location": forms.Select(
                attrs={
                    "class": "form-control form-control-md",
                    "data-mdb-validation": "true",
                    "v-model": "arrangement.location",
                }
            ),
            "audience": forms.Select(
                attrs={
                    "class": "form-control",
                    "data-mdb-placeholder": "Select audience",
                    "data-mdb-validation": "true",
                }
            ),
            "arrangement_type": forms.Select(
                attrs={"class": "form-control-md", "data-mdb-validation": "true"}
            ),
            "responsible": forms.Select(
                attrs={"class": "form-control-md", "data-mdb-validation": "true"}
            ),
            "status": forms.Select(attrs={"class": "form-control"}),
        }
