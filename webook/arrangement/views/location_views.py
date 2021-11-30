from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
)
from webook.arrangement.models import Location


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