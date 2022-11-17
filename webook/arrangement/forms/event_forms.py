from datetime import datetime
from typing import List, Optional, Tuple

import pytz
from django import forms
from django.forms import CharField, fields
from django.utils import timezone as dj_timezone

from webook.arrangement.models import Event, EventSerie, PlanManifest
from webook.utils.sph_gen import get_serie_positional_hash
from webook.utils.utc_to_current import utc_to_current

_ALWAYS_FIELDS = (
    "title",
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
    "before_buffer_title",
    "before_buffer_date",
    "before_buffer_start",
    "before_buffer_end",
    "after_buffer_title",
    "after_buffer_date",
    "after_buffer_start",
    "after_buffer_end",
    "status",
    "meeting_place",
    "meeting_place_en",
    "audience",
    "arrangement_type",
    "responsible",
    "display_text",
    "serie_position_hash",
    "parent_serie_position_hash",
    "start_before_collision_resolution",
    "end_before_collision_resolution",
    "title_before_collision_resolution",
)


class BaseEventForm(forms.ModelForm):
    before_buffer_title = forms.CharField(required=False)
    before_buffer_date = forms.DateField(required=False)
    before_buffer_start = forms.TimeField(required=False)
    before_buffer_end = forms.TimeField(required=False)

    after_buffer_title = forms.CharField(required=False)
    after_buffer_date = forms.DateField(required=False)
    after_buffer_start = forms.TimeField(required=False)
    after_buffer_end = forms.TimeField(required=False)

    title_before_collision_resolution = forms.CharField(required=False)
    start_before_collision_resolution = forms.DateTimeField(required=False)
    end_before_collision_resolution = forms.DateTimeField(required=False)

    serie_uuid = forms.CharField(required=False)
    serie_position_hash = forms.CharField(required=False)
    parent_serie_position_hash = forms.CharField(required=False)

    def save(self, commit: bool = True):
        if self.instance.serie is not None:
            """
            When a serie event has been edited it has become more specific - thus we want to degrade it to "association" status.
            This means that the more specific changes made here will not be altered by serie edits, and this event will not be deleted
            if the serie is.
            """
            self.instance.degrade_to_association_status(commit=False)

            super().save(commit)

        current_tz = pytz.timezone(str(dj_timezone.get_current_timezone()))

        serie_uuid = self.cleaned_data["serie_uuid"]
        pos_hash = self.cleaned_data["serie_position_hash"]
        par_pos_hash = self.cleaned_data["parent_serie_position_hash"]

        serie = None
        source_manifest = PlanManifest.objects.filter(internal_uuid=serie_uuid).last()

        self.instance.is_resolution = (
            self.instance.start_before_collision_resolution is not None
            and self.instance.end_before_collision_resolution is not None
        )

        if self.instance.associated_serie is not None:
            serie = self.instance.associated_serie
        elif serie_uuid is not None and source_manifest is not None:
            serie: EventSerie = source_manifest.eventserie_set.first()
            self.instance.associated_serie = serie

        if serie is not None:
            events_in_serie: List[Event] = serie.associated_events.all()

            parent_event: Event = None
            for event in events_in_serie:
                start = (
                    event.start_before_collision_resolution.astimezone(current_tz)
                    if event.start_before_collision_resolution
                    else event.start
                )
                end = (
                    event.end_before_collision_resolution.astimezone(current_tz)
                    if event.end_before_collision_resolution
                    else event.end
                )
                if pos_hash and par_pos_hash:
                    ev_hash = get_serie_positional_hash(
                        serie_uuid=serie_uuid,
                        event_title=event.title_before_collision_resolution
                        or event.title,
                        start=start,
                        end=end,
                    )

                    if ev_hash == par_pos_hash:
                        parent_event = event

                        self.instance.save()

                        is_before = self.instance.start < parent_event.start
                        if is_before:
                            parent_event.buffer_before_event = self.instance
                        else:
                            parent_event.buffer_after_event = self.instance

                        parent_event.save()

        if self.instance.is_buffer_event:
            if self.instance.before_buffer_for.exists():
                pre_buffering_event = self.instance.before_buffer_for.get()

                pre_buffering_event.before_buffer_title = (
                    self.instance.before_buffer_title
                )
                pre_buffering_event.before_buffer_date = (
                    self.instance.before_buffer_date
                )
                pre_buffering_event.before_buffer_start = utc_to_current(
                    self.instance.start
                ).strftime("%H:%M")
                pre_buffering_event.before_buffer_end = utc_to_current(
                    self.instance.end
                ).strftime("%H:%M")

                pre_buffering_event.save()
            if self.instance.after_buffer_for.exists():
                post_buffering_event = self.instance.after_buffer_for.get()

                post_buffering_event.after_buffer_title = (
                    self.instance.after_buffer_title
                )
                post_buffering_event.after_buffer_date = self.instance.after_buffer_date
                post_buffering_event.after_buffer_start = utc_to_current(
                    self.instance.start
                ).strftime("%H:%M")
                post_buffering_event.after_buffer_end = utc_to_current(
                    self.instance.end
                ).strftime("%H:%M")

                post_buffering_event.save()

        self.instance.save()
        self.instance.rooms.set(self.cleaned_data["rooms"])
        self.instance.people.set(self.cleaned_data["people"])

        _: Tuple[Optional[Event], Optional[Event]] = self.instance.refresh_buffers()

    class Meta:
        model = Event
        fields = _ALWAYS_FIELDS
        widgets = {
            "responsible": forms.Select(
                attrs={"class": "form-control form-control-lg"}
            ),
            "display_layouts": forms.CheckboxSelectMultiple(
                attrs={
                    "id": "display_layouts_create_event",
                    "name": "display_layouts_create_event",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control form-control-lg"}),
        }


class CreateEventForm(BaseEventForm):
    pass


class UpdateEventForm(BaseEventForm):
    class Meta:
        model = Event
        fields = ("id",) + _ALWAYS_FIELDS
        widgets = {
            "responsible": forms.Select(
                attrs={"class": "form-control form-control-lg"}
            ),
            "display_layouts": forms.CheckboxSelectMultiple(
                attrs={
                    "id": "display_layouts_create_event",
                    "name": "display_layouts_create_event",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control form-control-lg"}),
        }
