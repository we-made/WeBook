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
from webook.arrangement.models import ServiceType
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin


section_manifest = {
    "SECTION_TITLE": _("Service Types"),
    "SECTION_ICON": "fas fa-concierge-bell",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:servicetype_list"),
    "CRUDL_MAP": SectionCrudlPathMap(
        detail_url="arrangement:servicetype_detail",
        create_url="arrangement:servicetype_create",
        edit_url="arrangement:servicetype_edit",
        delete_url="arrangement:servicetype_delete",
        list_url="arrangement:servicetype_list",
    )
}


class ServiceTypeListView (LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    queryset = ServiceType.objects.all()
    template_name = "arrangement/servicetype/servicetype_list.html"
    section = section_manifest
    model = ServiceType
    section_subtitle = _("All Service Types")
    current_crumb_title = _("All Service Types")
    current_crumb_icon = "fas fa-list"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section["CRUDL_MAP"]
        return context

service_type_list_view = ServiceTypeListView.as_view()


class ServiceTypeDetailView(LoginRequiredMixin, CrumbMixin, DetailView):
    model = ServiceType
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/servicetype/servicetype_detail.html"
    section = section_manifest
    entity_name_attribute = "name"

service_type_detail_view = ServiceTypeDetailView.as_view()


class ServiceTypeUpdateView (LoginRequiredMixin, CrumbMixin, UpdateView):
    model = ServiceType
    fields = [
        "name"
    ]
    template_name = "arrangement/servicetype/servicetype_form.html"
    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = _("Edit")

service_type_update_view = ServiceTypeUpdateView.as_view()


class ServiceTypeCreateView (LoginRequiredMixin, CrumbMixin, CreateView):
    model = ServiceType
    fields = [
        "name"
    ]
    template_name = "arrangement/servicetype/servicetype_form.html"
    section = section_manifest
    current_crumb_title = _("New Servicetype")
    current_crumb_icon = "fas fa-plus"

service_type_create_view = ServiceTypeCreateView.as_view()


class ServiceTypeDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = ServiceType 
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/delete_view.html"

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:servicetype_list"
        )

    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = _("Delete")

service_type_delete_view = ServiceTypeDeleteView.as_view()