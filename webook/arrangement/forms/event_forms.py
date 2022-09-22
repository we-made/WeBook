from datetime import datetime
from typing import Optional, Tuple

import pytz
from django import forms
from django.forms import CharField, fields
from django.utils import timezone as dj_timezone

from webook.arrangement.models import Event
from webook.utils.utc_to_current import utc_to_current

_ALWAYS_FIELDS = ( "title",
                   "title_en",
                   "ticket_code",
                   "expected_visitors",
                   "actual_visitors",
                   "start",
                   "end",
                   "arrangement",
                   "color",
                   "sequence_guid",
                   "display_layouts",
                   "people",
                   "rooms",
                   "before_buffer_start",
                   "before_buffer_end",
                   "after_buffer_start",
                   "after_buffer_end",
                   "status",
                   "meeting_place",
                   "meeting_place_en",
                   "audience",
                   "arrangement_type",)


class BaseEventForm(forms.ModelForm):

    before_buffer_start = forms.TimeField(required=False)
    before_buffer_end = forms.TimeField(required=False)
    after_buffer_start = forms.TimeField(required=False)
    after_buffer_end = forms.TimeField(required=False)

    def save(self, commit: bool=True):
        if self.instance.serie is not None:
            """ 
            When a serie event has been edited it has become more specific - thus we want to degrade it to "association" status.
            This means that the more specific changes made here will not be altered by serie edits, and this event will not be deleted
            if the serie is.
            """
            self.instance.degrade_to_association_status(commit=False)

        super().save(commit)

        if self.instance.is_buffer_event:
            if self.instance.before_buffer_for.exists():
                pre_buffering_event = self.instance.before_buffer_for.get()
                pre_buffering_event.before_buffer_start = utc_to_current(self.instance.start).strftime("%H:%M")
                pre_buffering_event.before_buffer_end = utc_to_current(self.instance.end).strftime("%H:%M")
                pre_buffering_event.save()
            if self.instance.after_buffer_for.exists():
                post_buffering_event = self.instance.after_buffer_for.get()
                post_buffering_event.after_buffer_start = utc_to_current(self.instance.start).strftime("%H:%M")
                post_buffering_event.after_buffer_end = utc_to_current(self.instance.end).strftime("%H:%M")
                post_buffering_event.save()

        _ : Tuple[Optional[Event], Optional[Event]] = self.instance.refresh_buffers()

    class Meta:
        model = Event
        fields = _ALWAYS_FIELDS
        widgets = { 
            "display_layouts": forms.CheckboxSelectMultiple( attrs={'id': 'display_layouts_create_event', 'name': 'display_layouts_create_event'} ), 
            "status": forms.Select(attrs={'class': 'form-control form-control-lg'}),
        }


class CreateEventForm(BaseEventForm):
    pass


class UpdateEventForm(BaseEventForm):
    class Meta:
        model = Event
        fields = ( "id", ) + _ALWAYS_FIELDS
        widgets = { 
            "display_layouts": forms.CheckboxSelectMultiple( attrs={'id': 'display_layouts_create_event', 'name': 'display_layouts_create_event'} ), 
            "status": forms.Select(attrs={'class': 'form-control form-control-lg'}),
        }
