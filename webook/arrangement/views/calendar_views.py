from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    TemplateView
)
from webook.arrangement.models import Person, Location
from webook.utils.meta.meta_view_mixins import MetaMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Calendars"),
        section_icon= "fas fa-calendar",
        section_crumb_url=reverse("arrangement:arrangement_calendar")
    )


class CalendarSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class CalendarSamplesOverview (LoginRequiredMixin, CalendarSectionManifestMixin, MetaMixin, TemplateView):
    template_name = "arrangement/calendar/calendars_list.html"
    view_meta=ViewMeta(
        subtitle=_("Calendar Samples"),
        current_crumb_title=_("Calendar Samples")
    )

calendar_samples_overview = CalendarSamplesOverview.as_view()


class ArrangementCalendarView (LoginRequiredMixin, CalendarSectionManifestMixin, MetaMixin, TemplateView):
    template_name = "arrangement/calendar/arrangement_calendar.html"
    view_meta = ViewMeta(
        subtitle=_("Arrangement Calendar"),
        current_crumb_title=_("Arrangement Calendar")
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["locations"] = Location.objects.all()
        context["people"] = Person.objects.all()
        return context

arrangement_calendar_view = ArrangementCalendarView.as_view()