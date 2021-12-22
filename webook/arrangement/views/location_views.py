from typing import Any, Dict
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
from webook.arrangement.models import Location
from webook.arrangement.views.custom_views.crumb_view import MetaMixin
import json

from webook.utils.meta_utils.section_manifest import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Locations"),
        section_icon="fas fa-building",
        section_crumb_url=reverse("arrangement:location_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:location_detail",
            create_url="arrangement:location_create",
            edit_url="arrangement:location_edit",
            delete_url="arrangement:location_delete",
            list_url="arrangement:location_list",
        )
    )


class LocationSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class LocationListView(LoginRequiredMixin, LocationSectionManifestMixin, GenericListTemplateMixin, MetaMixin, ListView):
    queryset = Location.objects.all()
    model = Location
    view_meta = ViewMeta.Preset.table(Location)
    template_name = "arrangement/list_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

location_list_view = LocationListView.as_view()


class LocationDetailView(LoginRequiredMixin, LocationSectionManifestMixin, MetaMixin, DetailView):
    model = Location
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(Location)
    template_name = "arrangement/location/location_detail.html" 

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)

        current_location = self.get_object()
        rooms = list()
        for room in current_location.rooms.all():
            rooms.append(
                {
                    "id": f"R-{room.id}",
                    "title": f"{room.name}"
                }
            )
        ctx["resources_json"] = json.dumps(rooms)
        return ctx

location_detail_view = LocationDetailView.as_view()


class LocationUpdateView(LoginRequiredMixin, LocationSectionManifestMixin, MetaMixin, UpdateView):
    fields = [
        "name"
    ]
    view_meta = ViewMeta.Preset.edit(Location)
    template_name = "arrangement/location/location_form.html" 
    model = Location

location_update_view = LocationUpdateView.as_view()


class LocationCreateView(LoginRequiredMixin, LocationSectionManifestMixin, MetaMixin, CreateView):
    fields = [
        "name"
    ]
    view_meta = ViewMeta.Preset.create(Location)
    template_name = "arrangement/location/location_form.html" 
    model = Location

location_create_view = LocationCreateView.as_view()


class LocationDeleteView(LoginRequiredMixin, LocationSectionManifestMixin, MetaMixin, DeleteView):
    model = Location
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/delete_view.html"
    view_meta = ViewMeta.Preset.delete(Location)
    
    def get_success_url(self) -> str:
        return reverse(
            "arrangement:location_list"
        )

location_delete_view = LocationDeleteView.as_view()