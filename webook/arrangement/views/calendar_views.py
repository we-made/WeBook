from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
from webook.arrangement.models import Event, Person, Room
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin


section_manifest = {
    "SECTION_TITLE": _("Calendars"),
    "SECTION_ICON": "fas fa-calendar",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:arrangement_calendar")
}

class CalendarSamplesOverview (LoginRequiredMixin, CrumbMixin, TemplateView):
    template_name = "arrangement/calendar/calendars_list.html"
    section = section_manifest
    current_crumb_title = "Calendar Samples"
    section_subtitle = "Calendar Samples"

calendar_samples_overview = CalendarSamplesOverview.as_view()


class ArrangementCalendarView (LoginRequiredMixin, CrumbMixin, TemplateView):
    template_name = "arrangement/calendar/arrangement_calendar.html"
    section = section_manifest
    current_crumb_title = "Arrangement Calendar"
    section_subtitle = "Arrangement Calendar"


arrangement_calendar_view = ArrangementCalendarView.as_view()