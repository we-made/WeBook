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


section_manifest = {
    "SECTION_TITLE": _("Locations"),
    "SECTION_ICON": "fas fa-building",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:location_list")
}

class LocationListView(LoginRequiredMixin, ListView):
    queryset = Location.objects.all()
    template_name = "arrangement/location/location_list.html"

location_list_view = LocationListView.as_view()


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    slug_field = "slug"
    slug_url_kwarg = "slug"

    template_name = "arrangement/location/location_detail.html" 

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