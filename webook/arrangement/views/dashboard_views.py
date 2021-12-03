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
    "SECTION_TITLE": _("Dashboard"),
    "SECTION_ICON": "fas fa-chart-pie",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:dashboard")
}


class DashboardView (LoginRequiredMixin, CrumbMixin, TemplateView):
    template_name = "arrangement/dashboard/dashboard.html"
    section = section_manifest
    section_subtitle = "Welcome back!"

dashboard_view = DashboardView.as_view()