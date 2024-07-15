from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from webook.arrangement.models import RoomPreset


class RoomPresetCreateForm(forms.ModelForm):
    class Meta:
        model = RoomPreset
        fields = ('name', 'rooms')
        widgets = { "rooms": CheckboxSelectMultiple(), }
