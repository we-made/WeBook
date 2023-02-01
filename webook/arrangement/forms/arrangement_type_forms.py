from typing import Optional, Tuple

from django import forms

from webook.arrangement.models import ArrangementType

_ALWAYS_FIELDS = (
    "parent",
    "name",
    "name_en",
)


class BaseArrangementTypeForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=ArrangementType.objects.filter(parent__isnull=True),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    name_en = forms.CharField(max_length=255, required=False)

    class Meta:
        model = ArrangementType
        fields = _ALWAYS_FIELDS


class UpdateArrangementTypeForm(BaseArrangementTypeForm):
    pass


class CreateArrangementTypeForm(BaseArrangementTypeForm):
    pass
