from django import forms
from webook.arrangement.models import RoomPreset
from django.forms.widgets import CheckboxSelectMultiple


class RoomPresetCreateForm(forms.ModelForm ):
    class Meta:
        model = RoomPreset
        fields = ('name', 'rooms')
        widgets = { "rooms": CheckboxSelectMultiple(), }