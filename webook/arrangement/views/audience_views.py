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
from django.views.generic.edit import DeleteView
from webook.arrangement.models import Audience
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin

section_manifest = {
    "SECTION_TITLE": _("Audience"),
    "SECTION_ICON": "fas fa-user",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:audience_list")
}


class AudienceListView(LoginRequiredMixin, CrumbMixin, ListView):
    queryset = Audience.objects.all()
    template_name = "arrangement/audience/audience_list.html"
    section = section_manifest
    section_subtitle = _("All Audiences")
    current_crumb_title = "All Audiences"
    current_crumb_icon = "fas fa-list"

audience_list_view = AudienceListView.as_view()


class AudienceDetailView(LoginRequiredMixin, CrumbMixin, DetailView):
    model = Audience
    slug_field = "slug"
    slug_url_kwarg = "slug"
    section = section_manifest
    template_name = "arrangement/audience/audience_detail.html"
    entity_name_attribute = "name"

audience_detail_view = AudienceDetailView.as_view()


class AudienceCreateView(LoginRequiredMixin, CrumbMixin, CreateView):
    model = Audience
    fields = [
        "name"
    ]
    section = section_manifest
    template_name = "arrangement/audience/audience_form.html"
    current_crumb_title = "Create Audience"
    section_subtitle = "Create Audience"

audience_create_view = AudienceCreateView.as_view()


class AudienceUpdateView(LoginRequiredMixin, CrumbMixin, UpdateView):
    model = Audience
    fields = [
        "name"
    ]
    section = section_manifest
    template_name = "arrangement/audience/audience_form.html"

audience_update_view = AudienceUpdateView.as_view()


class AudienceDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = Audience
    template_name = "arrangement/delete_view.html"
    section = section_manifest

audience_delete_view = AudienceDeleteView.as_view()