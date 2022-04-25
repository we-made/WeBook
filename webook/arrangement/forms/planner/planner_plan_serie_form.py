from django import forms
from webook.arrangement.models import Arrangement, RoomPreset, Event
from django.forms.widgets import CheckboxSelectMultiple

from webook.screenshow.models import DisplayLayout


class PlannerPlanSerieForm(forms.Form):
    title = forms.CharField()
    title_en = forms.CharField()
    start = forms.TimeField()
    end = forms.TimeField()
    ticket_code = forms.CharField()
    expected_visitors = forms.IntegerField()
    
    display_layouts = forms.ModelMultipleChoiceField( 
        queryset=DisplayLayout.objects.all(),
        widget=CheckboxSelectMultiple
    )

    class Meta:
        widgets = { "display_layouts": CheckboxSelectMultiple(), }