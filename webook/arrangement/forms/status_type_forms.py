from typing import Optional, Tuple

from django import forms

from webook.arrangement.models import StatusType

_ALWAYS_FIELDS = ( "name",
                   "color", )

class BaseStatusTypeForm(forms.ModelForm):
    class Meta:
        model = StatusType
        fields = _ALWAYS_FIELDS


class UpdateStatusTypeForm(BaseStatusTypeForm):
    pass


class CreateStatusTypeForm(BaseStatusTypeForm):
    pass
