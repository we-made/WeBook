from typing import Any
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
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


section_manifest = SectionManifest(
    section_title=_("Rooms"),
    section_icon="fas fa-door-open",
    section_crumb_url=lambda: reverse("arrangement:room_list")
)


class RoomListView(LoginRequiredMixin, ListView):
    queryset = Room.objects.all()
    template_name = "arrangement/room/room_list.html"
    view_meta = ViewMeta.Preset.table(Room)

room_list_view = RoomListView.as_view()


class RoomDetailView(LoginRequiredMixin, DetailView):
    model = Room
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(Room)

    template_name = "arrangement/room/room_detail.html"

room_detail_view = RoomDetailView.as_view()


class RoomUpdateView(LoginRequiredMixin, UpdateView):
    fields = [
        "location",
        "name",
    ]
    view_meta = ViewMeta.Preset.edit(Room)

    template_name = "arrangement/room/room_form.html"

    model = Room

room_update_view = RoomUpdateView.as_view()


class RoomCreateView(LoginRequiredMixin, CreateView):
    fields = [
        "location",
        "name"
    ]
    view_meta = ViewMeta.Preset.create(Room)
    template_name = "arrangement/room/room_form.html"

    model = Room

    # def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
    #     print(request.data)
    #     return super().post(request, *args, **kwargs)

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
    view_meta = ViewMeta.Preset.delete(Room)

room_delete_view = RoomDeleteView.as_view()


class LocationRoomListView (LoginRequiredMixin, ListView):
    model = Location
    queryset = Room.objects.all()
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name="arrangement/room/partials/_location_room_list.html"

location_room_list_view = LocationRoomListView.as_view()