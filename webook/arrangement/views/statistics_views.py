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
from django.views.generic.edit import DeleteView
from webook.arrangement.models import Room
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin


section_manifest = {
    "SECTION_TITLE": _("Statistics"),
    "SECTION_ICON": "fas fa-graph",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:statistics_hub")
}
