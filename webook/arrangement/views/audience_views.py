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
from webook.arrangement.models import Arrangement, Audience
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin


section_manifest = {
    "SECTION_TITLE": _("Audience"),
    "SECTION_ICON": "fas fa-user",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:audience_list"),
    "CRUDL_MAP": SectionCrudlPathMap(
        detail_url="arrangement:audience_detail",
        create_url="arrangement:audience_create",
        edit_url="arrangement:audience_edit",
        delete_url="arrangement:audience_delete",
        list_url="arrangement:audience_list",
    )
}

class AudienceListView(LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    template_name = "arrangement/list_view.html"
    model = Audience
    queryset = Audience.objects.all()
    section = section_manifest
    section_subtitle = _("All Audiences")
    current_crumb_title = _("All Audiences")
    current_crumb_icon = "fas fa-list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section["CRUDL_MAP"]
        return context

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
    current_crumb_title = _("Create Audience")
    section_subtitle = _("Create Audience")

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