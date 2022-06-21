from django import forms
from django.forms import fields
from django.forms.widgets import CheckboxSelectMultiple

from webook.arrangement.models import Arrangement, Event, RoomPreset


class PlannerUpdateEventForm(forms.ModelForm):
    people = fields.CharField(max_length=5024, required=False)
    rooms = fields.CharField(max_length=5024, required=False)

    def save(self, commit=True):
        people_comma_separated_str = self.cleaned_data["people"]
        rooms_comma_separated_str = self.cleaned_data["rooms"]

        is_valid = lambda str: str is not None and len(str) > 0 and str != "undefined"

        if is_valid(people_comma_separated_str):
            self.instance.people.add(*[int(x) for x in people_comma_separated_str.split(",")])
        if is_valid(rooms_comma_separated_str):
            self.instance.rooms.add(*[int(x) for x in rooms_comma_separated_str.split(",")])

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
        fields = (
            "title",
            "title_en",
            "start",
            "end",
            "ticket_code",
            "expected_visitors",
            "actual_visitors",
            "display_layouts",)
        widgets = { "display_layouts": CheckboxSelectMultiple(), }
