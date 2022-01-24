from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import query
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core import serializers
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
import json
from django.views.generic.edit import DeleteView
from webook.arrangement.models import Event, Location, Person, Room
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
    ]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        super().post(request, *args, **kwargs)
        people = self.request.POST.get("people")
        
        return JsonResponse({"id": self.object.id})

    def get_success_url(self) -> str:
        people = self.request.POST.get("people")
        
        print(people)

        if (people is None or len(people) == 0):
            return
        
        obj = self.object
        people = people.split(',')
        for person in people:
            obj.people.add(Person.objects.get(id=person))
        obj.save()
        pass

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
    ]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def get_success_url(self) -> str:
        people = self.request.POST.get("people")
        if (people is None or len(people) == 0):
            return

        obj = self.object
        people = people.split(',')
        for person in people:
            obj.people.add(Person.objects.get(id=person))
        obj.save()
        pass

plan_update_event = PlanUpdateEvent.as_view()


class PlanGetEvents (LoginRequiredMixin, ListView):
    
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(arrangement_id=request.GET["arrangement_id"]).only("title", "start", "end", "color", "people")
        response = serializers.serialize("json", events, fields=["title", "start", "end", "color", "people"])
        return JsonResponse(response, safe=False)

plan_get_events = PlanGetEvents.as_view()


class PlanDeleteEvent (LoginRequiredMixin, DeleteView):
    model = Event
    
    def get_success_url(self) -> str:
        pass

plan_delete_event = PlanDeleteEvent.as_view()