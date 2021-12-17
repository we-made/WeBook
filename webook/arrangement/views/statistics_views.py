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
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


section_manifest = SectionManifest(
    section_title=_("Statistics"),
    section_icon="fas fa-graph",
    section_crumb_url=lambda: reverse("arrangement:statistics_hub"),
)