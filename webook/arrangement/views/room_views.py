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
from webook.arrangement.models import Room


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
    ]

    template_name = "arrangement/room/room_form.html"

    model = Room

room_update_view = RoomUpdateView.as_view()


class RoomCreateView(LoginRequiredMixin, CreateView):
    fields = [
        "location",
        "name"
    ]

    template_name = "arrangement/room/room_form.html"

    model = Room

room_create_view = RoomCreateView.as_view()