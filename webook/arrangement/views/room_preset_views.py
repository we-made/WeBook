from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import query
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.contrib import messages
from django.http.response import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from webook.arrangement.views.mixins.multi_redirect_mixin import MultiRedirectMixin
from django.core import serializers, exceptions
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
from django.views.decorators.http import require_http_methods
import json
from django.views.generic.edit import DeleteView
from webook.arrangement.forms.cancel_service_requisition_form import CancelServiceRequisitionForm
from webook.arrangement.forms.loosely_order_service_form import LooselyOrderServiceForm
from webook.arrangement.forms.requisition_person_form import RequisitionPersonForm
from webook.arrangement.forms.order_service_form import OrderServiceForm
from webook.arrangement.forms.reset_service_requisition_form import ResetRequisitionForm
from webook.arrangement.forms.room_presets.room_preset_create_form import RoomPresetCreateForm
from webook.arrangement.models import Event, Location, Person, Room, LooseServiceRequisition, RoomPreset, ServiceRequisition
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap
from django.http import HttpResponseBadRequest, Http404


def get_section_manifest():
    return SectionManifest(
        section_title=_("Room Presets"),
        section_icon="fas fa-layer-group",
        section_crumb_url=reverse("arrangement:room_preset_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url=None,
            create_url="arrangement:room_preset_create",
            edit_url="arrangement:room_preset_update",
            delete_url="arrangement:room_preset_delete",
            list_url="arrangement:room_preset_list",
        )
    )

class RoomPresetsSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class RoomPresetsListView(LoginRequiredMixin, RoomPresetsSectionManifestMixin, GenericListTemplateMixin, MetaMixin, ListView):
    template_name = "arrangement/list_view.html"
    model = RoomPreset
    queryset = RoomPreset.objects.all()
    view_meta = ViewMeta.Preset.table(RoomPreset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

room_presets_listview = RoomPresetsListView.as_view()


class RoomPresetDetailView(LoginRequiredMixin, RoomPresetsSectionManifestMixin, GenericListTemplateMixin, MetaMixin, DetailView):
    template_name="arrangement/room_presets/detail.html"
    model = RoomPreset
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(RoomPreset)

room_preset_detail_view = RoomPresetDetailView.as_view()


class RoomPresetCreateView(LoginRequiredMixin, RoomPresetsSectionManifestMixin, MetaMixin, MultiRedirectMixin,  CreateView):
    form_class = RoomPresetCreateForm
    model = RoomPreset
    template_name="arrangement/room_presets/form.html"
    view_meta = ViewMeta.Preset.create(RoomPreset)

    success_urls_and_messages = { 
        "submitAndNew": { 
            "url": reverse_lazy( "arrangement:room_preset_create" ),
            "msg": _("Successfully created entity")
        },
        "submit": { 
            "url": reverse_lazy("arrangement:room_preset_list"),
        }
    }

room_preset_create_view = RoomPresetCreateView.as_view()


class RoomPresetUpdateView(LoginRequiredMixin, RoomPresetsSectionManifestMixin, MetaMixin, UpdateView):
    form_class = RoomPresetCreateForm
    model = RoomPreset

    template_name="arrangement/room_presets/form.html"
    view_meta = ViewMeta.Preset.edit(RoomPreset)

    def get_success_url(self) -> str:
        return reverse("arrangement:room_preset_list")

room_preset_update_view = RoomPresetUpdateView.as_view()


class RoomPresetDeleteView(LoginRequiredMixin, RoomPresetsSectionManifestMixin, MetaMixin, DeleteView):
    model = RoomPreset
    view_meta = ViewMeta.Preset.delete(RoomPreset)
    template_name = "arrangement/delete_view.html"

room_preset_delete_view = RoomPresetDeleteView.as_view()
