from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
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
from webook.arrangement.models import Location, Room
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
import json

section_manifest = {
    "SECTION_TITLE": _("Rooms"),
    "SECTION_ICON": "fas fa-door-open",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:room_list")
}

class RoomListView(LoginRequiredMixin, ListView):
    queryset = Room.objects.all()
    template_name = "arrangement/room/room_list.html"

room_list_view = RoomListView.as_view()


class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    slug_field = "slug"
    slug_url_kwarg = "slug"

    template_name = "arrangement/room/room_detail.html"

room_detail_view = RoomDetailView.as_view()


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    fields = [
        "location",
        "name",
        "max_capacity",
    ]

    template_name = "arrangement/room/room_form.html"

    model = Room

room_update_view = RoomUpdateView.as_view()


class RoomCreateView(LoginRequiredMixin, CreateView):
    fields = [
        "location",
        "name",
        "max_capacity",
    ]

    template_name = "arrangement/room/room_form.html"

    model = Room

room_create_view = RoomCreateView.as_view()


class RoomDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = Room
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/delete_view.html"
    
    def get_success_url(self) -> str:
        return reverse(
            "arrangement:room_list"
        )

    section = section_manifest
    entity_name_attribute = "name"
    section_subtitle_prefix = _("Delete")

room_delete_view = RoomDeleteView.as_view()


class LocationRoomListView (LoginRequiredMixin, ListView):
    model = Room
    template_name="arrangement/room/partials/_location_room_list.html"

    def get_queryset(self):
        location = self.request.GET.get('location')
        return Room.objects.filter(
            location=location
        )
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context["location"] = self.request.GET.get('location')
        return context

location_room_list_view = LocationRoomListView.as_view()