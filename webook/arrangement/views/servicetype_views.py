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
from webook.utils.meta_utils.section_manifest import SectionManifest
from webook.arrangement.models import ServiceType
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils.section_manifest import ViewMeta


section_manifest = SectionManifest(
    section_title=_("Service Types"),
    section_icon="fas fa-concierge-bell",
    section_crumb_url=lambda: reverse("arrangement:servicetype_list"),
    crudl_map=SectionCrudlPathMap(
        detail_url="arrangement:servicetype_detail",
        create_url="arrangement:servicetype_create",
        edit_url="arrangement:servicetype_edit",
        delete_url="arrangement:servicetype_delete",
        list_url="arrangement:servicetype_list",
    )
)


class ServiceTypeListView (LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    queryset = ServiceType.objects.all()
    template_name = "arrangement/list_view.html"
    section = section_manifest
    model = ServiceType
    view_meta = ViewMeta.Preset.table(ServiceType)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

service_type_list_view = ServiceTypeListView.as_view()


class ServiceTypeDetailView(LoginRequiredMixin, CrumbMixin, DetailView):
    model = ServiceType
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/servicetype/servicetype_detail.html"
    section = section_manifest
    view_meta = ViewMeta.Preset.detail(ServiceType)

service_type_detail_view = ServiceTypeDetailView.as_view()


class ServiceTypeUpdateView (LoginRequiredMixin, CrumbMixin, UpdateView):
    model = ServiceType
    fields = [
        "name"
    ]
    template_name = "arrangement/servicetype/servicetype_form.html"
    section = section_manifest
    view_meta = ViewMeta.Preset.edit(ServiceType)

service_type_update_view = ServiceTypeUpdateView.as_view()


class ServiceTypeCreateView (LoginRequiredMixin, CrumbMixin, CreateView):
    model = ServiceType
    fields = [
        "name"
    ]
    template_name = "arrangement/servicetype/servicetype_form.html"
    section = section_manifest
    view_meta = ViewMeta.Preset.create(ServiceType)

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
    view_meta = ViewMeta.Preset.delete(ServiceType)

service_type_delete_view = ServiceTypeDeleteView.as_view()