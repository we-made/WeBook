from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import query
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
from webook.arrangement.forms.order_service_form import OrderServiceForm
from webook.arrangement.models import Event, Location, Person, Room, LooseServiceRequisition
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Planning"),
        section_icon= "fas fa-ruler",
        section_crumb_url=reverse("arrangement:arrangement_calendar")
    )


class PlannerSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class PlannerView (LoginRequiredMixin, PlannerSectionManifestMixin, MetaMixin, TemplateView):
    template_name = "arrangement/planner/planner.html"
    view_meta = ViewMeta(
        subtitle="Planner",
        current_crumb_title="Planner"
    )

planner_view = PlannerView.as_view()

class PlanArrangementView(LoginRequiredMixin, PlannerSectionManifestMixin, MetaMixin, TemplateView):
    template_name = "arrangement/planner/plan_arrangement.html"

plan_arrangement_view = PlanArrangementView.as_view()


class PlanCreateEvent (LoginRequiredMixin, CreateView):
    model = Event
    fields = [
        "title",
        "start",
        "end",
        "arrangement",
        "color",
        "sequence_guid",
    ]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        super().post(request, *args, **kwargs)
        return JsonResponse({"id": self.object.id})

    def get_success_url(self) -> str:
        people = self.request.POST.get("people")
        rooms = self.request.POST.get("rooms")
        loose_requisitions = self.request.POST.get("loose_requisitions")

        obj = self.object

        if (people is not None and len(people) > 0):
            people = people.split(',')
            for personId in people:
                obj.people.add(Person.objects.get(id=personId))
        
        if (rooms is not None and len(rooms) > 0):
            rooms = rooms.split(',')
            for roomId in rooms:
                obj.rooms.add(Room.objects.get(id=roomId))

        if (loose_requisitions is not None and len(loose_requisitions) > 0):
            loose_requisitions = loose_requisitions.split(",")
            for lreqId in loose_requisitions:
                obj.loose_requisitions.add(LooseServiceRequisition.objects.get(id=lreqId))

        obj.save()

plan_create_event = PlanCreateEvent.as_view()


class PlanUpdateEvent (LoginRequiredMixin, UpdateView):
    model = Event
    template_name="arrangement/event/event_form.html"
    fields = [
        "id",
        "title",
        "start",
        "end",
        "arrangement",
        "color",
        "sequence_guid",
    ]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def get_success_url(self) -> str:
        people = self.request.POST.get("people")
        rooms = self.request.POST.get("rooms")

        if ((people is None or people == "undefined") and (rooms is None or rooms == "undefined")):
            return

        obj = self.object
        obj.people.clear()
        obj.rooms.clear()

        if (people is not None and len(people) > 0 and people != "undefined"):
            people = people.split(',')
            for personId in people:
                obj.people.add(Person.objects.get(id=personId))
        
        if (rooms is not None and len(rooms) > 0 and rooms != "undefined"):
            rooms = rooms.split(',')
            for roomId in rooms:
                obj.rooms.add(Room.objects.get(id=roomId))

        obj.save()

plan_update_event = PlanUpdateEvent.as_view()


class PlanGetEvents (LoginRequiredMixin, ListView):
    
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(arrangement_id=request.GET["arrangement_id"]).only("title", "start", "end", "color", "people", "rooms", "loose_requisitions", "sequence_guid")
        response = serializers.serialize("json", events, fields=["title", "start", "end", "color", "people", "rooms", "loose_requisitions", "sequence_guid"])
        return JsonResponse(response, safe=False)

plan_get_events = PlanGetEvents.as_view()


class PlanOrderService(LoginRequiredMixin, FormView):
    form_class = OrderServiceForm
    template_name = "_blank.html"

    def get_success_url(self) -> str:
        return reverse("arrangement:arrangement_list")

    def form_invalid(self, form) -> HttpResponse:
        print(" >> OrderServiceForm invalid")
        return super().form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        form.save()
        return super().form_valid(form)

plan_order_service_view = PlanOrderService.as_view()


class PlanDeleteEvent (LoginRequiredMixin, DeleteView):
    model = Event
    
    def get_success_url(self) -> str:
        pass

plan_delete_event = PlanDeleteEvent.as_view()


class PlanDeleteEvents (LoginRequiredMixin, View):
    model = Event

    def post(self, request, *args, **kwargs):
        eventIds = request.POST.get("eventIds", "")
        eventIds = eventIds.split(",")

        if (eventIds is None):
            raise exceptions.BadRequest()
        
        for id in eventIds:
            Event.objects.filter(pk=id).delete()

        return JsonResponse({ 'affected': len(eventIds) })
            
plan_delete_events = PlanDeleteEvents.as_view()