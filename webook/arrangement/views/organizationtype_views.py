from typing import List
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
from webook.arrangement.models import OrganizationType
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin


section_manifest = {
    "SECTION_TITLE": _("Organization Types"),
    "SECTION_ICON": "fas fa-object-group",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:organizationtype_list"),
    "CRUDL_MAP": SectionCrudlPathMap(
        detail_url="arrangement:organizationtype_detail",
        create_url="arrangement:organizationtype_create",
        edit_url="arrangement:organizationtype_edit",
        delete_url="arrangement:organizationtype_delete",
        list_url="arrangement:organizationtype_list",
    )
}


class OrganizationTypeListView (LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    queryset = OrganizationType.objects.all()
    template_name = "arrangement/list_view.html"
    model = OrganizationType
    section = section_manifest
    section_subtitle = _("All Organization Types")
    current_crumb_title = _("All Organization Types")
    current_crumb_icon = "fas fa-list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section["CRUDL_MAP"]
        return context

organization_type_list_view = OrganizationTypeListView.as_view()


class OrganizationTypeDetailView(LoginRequiredMixin, CrumbMixin, DetailView):
    model = OrganizationType
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/organizationtype/organizationtype_detail.html"
    section = section_manifest
    entity_name_attribute = "name"

organization_type_detail_view = OrganizationTypeDetailView.as_view()


class OrganizationTypeUpdateView (LoginRequiredMixin, CrumbMixin, UpdateView):
    model = OrganizationType
    fields = [
        "name"
    ]
    template_name = "arrangement/organizationtype/organizationtype_form.html"
    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = "Edit"

organization_type_update_view = OrganizationTypeUpdateView.as_view()


class OrganizationTypeCreateView (LoginRequiredMixin, CrumbMixin, CreateView):
    model = OrganizationType
    fields = [
        "name"
    ]
    template_name = "arrangement/organizationtype/organizationtype_form.html"
    section = section_manifest
    current_crumb_title = _("New Organization Type")
    current_crumb_icon = "fas fa-plus"

organization_type_create_view = OrganizationTypeCreateView.as_view()


class OrganizationTypeDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = OrganizationType 
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/delete_view.html"

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:organization_list"
        )

    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = _("Delete")

organization_type_delete_view = OrganizationTypeDeleteView.as_view()