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
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
import json

from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin


section_manifest = {
    "SECTION_TITLE": _("Locations"),
    "SECTION_ICON": "fas fa-building",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:location_list"),
    "CRUDL_MAP": SectionCrudlPathMap(
        detail_url="arrangement:organization_detail",
        create_url="arrangement:organization_create",
        edit_url="arrangement:organization_edit",
        delete_url="arrangement:organization_delete",
        list_url="arrangement:organization_list",
    )
}

class LocationListView(LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    queryset = Location.objects.all()
    model = Location
    section = section_manifest
    section_subtitle = _("All Locations")
    current_crumb_title = _("All Locations")
    current_crumb_icon = "fas fa-list"
    template_name = "arrangement/list_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section["CRUDL_MAP"]
        return context

location_list_view = LocationListView.as_view()


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    slug_field = "slug"
    slug_url_kwarg = "slug"

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


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    fields = [
        "name"
    ]

    template_name = "arrangement/location/location_form.html" 

    model = Location

location_update_view = LocationUpdateView.as_view()


class LocationCreateView(LoginRequiredMixin, CreateView):
    fields = [
        "name"
    ]

    template_name = "arrangement/location/location_form.html" 

    model = Location

location_create_view = LocationCreateView.as_view()


class LocationDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = Location
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/delete_view.html"

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:location_list"
        )

    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = _("Delete")

location_delete_view = LocationDeleteView.as_view()