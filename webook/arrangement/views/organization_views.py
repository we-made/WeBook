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
from webook.arrangement.models import Organization
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin


section_manifest = {
    "SECTION_TITLE": _("Organizations"),
    "SECTION_ICON": "fas fa-dollar-sign",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:organization_list"),
    "CRUDL_MAP": SectionCrudlPathMap(
        detail_url="arrangement:organization_detail",
        create_url="arrangement:organization_create",
        edit_url="arrangement:organization_edit",
        delete_url="arrangement:organization_delete",
        list_url="arrangement:organization_list",
    )
}

class OrganizationListView(LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    queryset = Organization.objects.all()
    template_name = "arrangement/list_view.html"
    section = section_manifest
    model = Organization
    section_subtitle = _("All Organizations")
    current_crumb_title = _("All Organizations")
    current_crumb_icon = "fas fa-list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section["CRUDL_MAP"]
        return context

organization_list_view = OrganizationListView.as_view()


class OrganizationDetailView(LoginRequiredMixin, DetailView):
    model = Organization
    slug_field = "slug"
    slug_url_kwarg = "slug"

    template_name = "arrangement/organization/organization_detail.html"

organization_detail_view = OrganizationDetailView.as_view()


class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    fields = [
        "organization_number",
        "name",
        "organization_type",
    ]

    model = Organization

    template_name = "arrangement/organization/organization_form.html"

organization_update_view = OrganizationUpdateView.as_view()


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    fields = [
        "organization_number",
        "name",
        "organization_type",
    ]

    model = Organization

    template_name = "arrangement/organization/organization_form.html"

organization_create_view = OrganizationCreateView.as_view()


class OrganizationDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = Organization
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name="arrangement/delete_view.html"

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:organization_list"
        )

    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = _("Delete")

organization_delete_view = OrganizationDeleteView.as_view()