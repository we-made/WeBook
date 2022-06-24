from django import forms
from django.forms import CharField, fields

from webook.arrangement.models import Event

_ALWAYS_FIELDS = ( "title",
                   "title_en",
                   "ticket_code",
                   "expected_visitors",
                   "start",
                   "end",
                   "arrangement",
                   "color",
                   "sequence_guid",
                   "display_layouts",
                   "people",
                   "rooms",)


class BaseEventForm(forms.ModelForm):
    def save(self, commit: bool=True):
        if self.instance.serie is not None:
            """ 
            When a serie event has been edited it has become more specific - thus we want to degrade it to "association" status.
            This means that the more specific changes made here will not be altered by serie edits, and this event will not be deleted
            if the serie is.
            """
            self.instance.degrade_to_association_status(commit=False)

        super().save(commit)


    class Meta:
        model = Event
        fields = _ALWAYS_FIELDS
        widgets = { 
            "display_layouts": forms.CheckboxSelectMultiple( attrs={'id': 'display_layouts_create_event', 'name': 'display_layouts_create_event'} ), 
        }


class CreateEventForm(BaseEventForm):
    pass


class UpdateEventForm(BaseEventForm):
    class Meta:
        model = Event
        fields = ( "id", ) + _ALWAYS_FIELDS
        widgets = { 
            "display_layouts": forms.CheckboxSelectMultiple( attrs={'id': 'display_layouts_create_event', 'name': 'display_layouts_create_event'} ), 
        }
