from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
)
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from webook.arrangement.models import Location
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin


section_manifest = {
    "SECTION_TITLE": _("Insight"),
    "SECTION_ICON": "fas fa-chart-pie",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:dashboard")
}


class GlobalTimelineView (LoginRequiredMixin, CrumbMixin, TemplateView):
    section = section_manifest
    section_subtitle = "Global Timeline"
    current_crumb_title = "Global Timeline"
    template_name = "arrangement/insights/global_timeline.html"

global_timeline_view = GlobalTimelineView.as_view()