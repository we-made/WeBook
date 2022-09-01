from django import forms
from typing import Optional, Tuple
from webook.arrangement.models import ArrangementType


_ALWAYS_FIELDS = ( "parent",
                   "name",
                   "name_en" )


class BaseArrangementTypeForm(forms.ModelForm):
    class Meta:
        model = ArrangementType
        fields =  _ALWAYS_FIELDS


class UpdateArrangementTypeForm(BaseArrangementTypeForm):
    pass


class CreateArrangementTypeForm(BaseArrangementTypeForm):
    pass