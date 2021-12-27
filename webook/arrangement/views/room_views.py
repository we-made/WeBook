from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
from webook.arrangement.models import Room
from django.views.generic.edit import DeleteView
from webook.utils.meta.meta_view_mixins import MetaMixin, GenericListTemplateMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Rooms"),
        section_icon="fas fa-door-open",
        section_crumb_url=reverse("arrangement:room_list")
    )


class RoomSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class RoomListView(LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, ListView):
    queryset = Room.objects.all()
    template_name = "arrangement/room/room_list.html"
    view_meta = ViewMeta.Preset.table(Room)

room_list_view = RoomListView.as_view()


class RoomUpdateView(LoginRequiredMixin, RoomSectionManifestMixin, MetaMixin, UpdateView):
    fields = [
        "location",
        "name",
    ]
    view_meta = ViewMeta.Preset.edit(Room)
    template_name = "arrangement/room/room_form.html"
    model = Room

room_update_view = RoomUpdateView.as_view()