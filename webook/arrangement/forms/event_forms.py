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

    rooms_cs = CharField(max_length=5000, required=False)
    people_cs = CharField(max_length=5000, required=False)
    display_layouts_cs = CharField(max_length=5000, required=False)

    def save(self, commit=True):
        if self.instance.serie is not None:
            """ 
            When a serie event has been edited it has become more specific - thus we want to degrade it to "association" status.
            This means that the more specific changes made here will not be altered by serie edits, and this event will not be deleted
            if the serie is.
            """
            self.instance.degrade_to_association_status(commit=False)

        parse_comma_sep_string = lambda comma_sep_str: [int(x) for x in comma_sep_str.split(",") if x] if comma_sep_str else []

        super().save(commit)

        self.instance.rooms.set(parse_comma_sep_string(self.cleaned_data["rooms_cs"]))
        self.instance.people.set(parse_comma_sep_string(self.cleaned_data["people_cs"]))
        self.instance.display_layouts.set(parse_comma_sep_string(self.cleaned_data["display_layouts_cs"]))

        self.instance.save()


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
