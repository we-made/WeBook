import json
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)
from django.views.generic.edit import DeleteView

from webook.arrangement.models import BusinessHour, Location, Room
from webook.arrangement.views.generic_views.archive_view import (
    ArchiveView,
    JsonArchiveView,
)
from webook.arrangement.views.generic_views.json_form_view import (
    JsonFormView,
    JsonModelFormMixin,
)
from webook.arrangement.views.generic_views.search_view import SearchView
from webook.authorization_mixins import PlannerAuthorizationMixin
from webook.utils.meta_utils import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta_utils.meta_mixin import MetaMixin


def get_section_manifest():
    return SectionManifest(
        section_title=_("Rooms"),
        section_icon="fas fa-door-open",
        section_crumb_url=reverse("arrangement:room_list"),
    )


class RoomSectionManifestMixin(PlannerAuthorizationMixin):
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class RoomListView(LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, ListView):
    queryset = Room.objects.all()
    template_name = "arrangement/room/room_list.html"
    view_meta = ViewMeta.Preset.table(Room)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


room_list_view = RoomListView.as_view()


class RoomDetailView(
    LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, DetailView
):
    model = Room
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(Room)
    template_name = "arrangement/room/room_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Days"] = BusinessHour.Days._member_names_
        return context


room_detail_view = RoomDetailView.as_view()


class RoomDetailJsonView(LoginRequiredMixin, RoomSectionManifestMixin, DetailView):
    model = Room
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        data = json.dumps(
            {
                "id": self.object.id,
                "slug": self.object.slug,
                "name": self.object.name,
                "name_en": self.object.name_en,
                "max_capacity": self.object.max_capacity,
                "location": self.object.location.id,
                "location_name": self.object.location.name,
                "is_exclusive": self.object.is_exclusive,
                "has_screen": self.object.has_screen,
            }
        )
        return HttpResponse(data, content_type="appliwation/json")


room_detail_json_view = RoomDetailJsonView.as_view()


class RoomUpdateView(
    LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, UpdateView
):
    fields = [
        "location",
        "name",
        "name_en",
        "is_exclusive",
        "has_screen",
        "max_capacity",
    ]
    view_meta = ViewMeta.Preset.edit(Room)
    template_name = "arrangement/room/room_form.html"
    model = Room


room_update_view = RoomUpdateView.as_view()


class RoomCreateJsonView(LoginRequiredMixin, CreateView, JsonModelFormMixin):
    model = Room
    fields = [
        "location",
        "name",
        "name_en",
        "max_capacity",
        "has_screen",
        "is_exclusive",
    ]


room_create_json_view = RoomCreateJsonView.as_view()


class RoomUpdateJsonView(LoginRequiredMixin, UpdateView, JsonModelFormMixin):
    model = Room
    fields = [
        "location",
        "name",
        "name_en",
        "max_capacity",
        "has_screen",
        "is_exclusive",
    ]


room_update_json_view = RoomUpdateJsonView.as_view()


class RoomCreateView(
    LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, CreateView
):
    fields = [
        "location",
        "name",
        "name_en",
        "max_capacity",
        "has_screen",
        "is_exclusive",
    ]
    view_meta = ViewMeta.Preset.create(Room)
    template_name = "arrangement/room/room_form.html"
    model = Room


room_create_view = RoomCreateView.as_view()


class RoomDeleteView(
    LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, JsonArchiveView
):
    model = Room
    slug_field = "slug"
    slug_url_kwarg = "slug"


room_delete_view = RoomDeleteView.as_view()


class SearchRoomsAjax(LoginRequiredMixin, SearchView):
    model = Room

    def search(self, search_term):
        rooms = []

        if search_term == "":
            rooms = Room.objects.all()
        else:
            rooms = Room.objects.filter(name__contains=search_term)

        return rooms


search_room_ajax_view = SearchRoomsAjax.as_view()


class LocationRoomListView(LoginRequiredMixin, ListView):
    model = Location
    queryset = Room.objects.all()
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/room/partials/_location_room_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        location_id = self.kwargs.get("location")
        context["LOCATION"] = Location.objects.get(id=location_id)

        return context

    def get_queryset(self):
        return (
            super().get_queryset().filter(location_id=self.request.GET.get("location"))
        )


location_room_list_view = LocationRoomListView.as_view()


class SearchRoomsAjax(LoginRequiredMixin, SearchView):
    model = Room

    def search(self, search_term):
        search_term.replace(" ", "")

        rooms = []

        if search_term == "":
            rooms = Room.objects.all()
        else:
            rooms = Room.objects.filter(name__contains=search_term)

        return rooms


search_rooms_ajax_view = SearchRoomsAjax.as_view()
