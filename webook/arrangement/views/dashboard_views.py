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
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap

section_manifest = SectionManifest(
    section_title=_("Dashboard"),
    section_icon="fas fa-chart-pie",
    section_crumb_url=lambda: reverse("arrangement:dashboard")
)


class DashboardView (LoginRequiredMixin, CrumbMixin, TemplateView):
    template_name = "arrangement/dashboard/dashboard.html"
    section = section_manifest

    view_meta = ViewMeta(
        subtitle=_("Welcome back!")
    )

dashboard_view = DashboardView.as_view()