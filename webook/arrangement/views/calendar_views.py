import datetime
from typing import Any, List

from dateutil import parser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.db import connection
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
)

from webook.arrangement.exceptions import UserHasNoPersonException
from webook.arrangement.models import Event, Location, Person, Room
from webook.utils.meta_utils import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta_utils.meta_mixin import MetaMixin


def get_section_manifest():
    return SectionManifest(
        section_title=_("Calendars"),
        section_icon="fas fa-calendar",
        section_crumb_url=reverse("arrangement:arrangement_calendar"),
    )


class CalendarSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class ResourceSourceViewMixin(ListView):
    def convert_resource_to_fc_resource(self, resource):
        raise Exception("convert_resource_to_fc_resource not implemented")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return JsonResponse(
            [
                self.convert_resource_to_fc_resource(resource)
                for resource in self.get_queryset().all()
            ],
            safe=False,
        )


class RoomBasedResourceSourceView:
    def convert_resource_to_fc_resource(self, resource):
        return {
            "id": resource.slug,
            "title": resource.name,
            "max_capacity": resource.max_capacity,
            "is_exclusive": resource.is_exclusive,
            "has_screen": resource.has_screen,
        }


class AllPeopleResourceSourceView(ResourceSourceViewMixin):
    model = Person

    def convert_resource_to_fc_resource(self, resource):
        return {
            "id": resource.slug,
            "title": resource.full_name,
        }


all_people_resource_source_view = AllPeopleResourceSourceView.as_view()


class AllRoomsResourceSourceView(ResourceSourceViewMixin):
    model = Room

    def convert_resource_to_fc_resource(self, resource):
        return {
            "id": resource.slug,
            "title": resource.name,
        }


all_rooms_resource_source_view = AllRoomsResourceSourceView.as_view()


class AllLocationsResourceSourceView(ResourceSourceViewMixin):
    model = Location

    def convert_resource_to_fc_resource(self, resource):
        return {"id": resource.slug, "title": resource.name}


all_locations_resource_source_view = AllLocationsResourceSourceView.as_view()


class RoomsOnLocationResourceSourceView(
    RoomBasedResourceSourceView, ResourceSourceViewMixin
):
    model = Room

    def get_queryset(self):
        location_slug = self.request.GET.get("location", None)

        if location_slug is None:
            raise SuspiciousOperation("No location supplied, please supply a location.")

        location = Location.objects.get(slug=location_slug)

        return location.rooms


rooms_on_location_resource_source_view = RoomsOnLocationResourceSourceView.as_view()


class EventSourceViewMixin(ListView):
    """A mixin for views that serve the express purpose of serving events to FullCalendar calendars

    Attributes:
        handle_time_constraints_on_get (bool): A boolean designating if datetime constraints should be handled in the GET method. Set to False if you want to get all regardless of supplied time constraints, or do your own handling of constraints in the get_queryset method.
    """

    handle_time_constraints_on_get = True

    def convert_event_to_fc_event(self, event: Event):
        """Converts an event to a FullCalendar worthy event"""
        return {
            "title": event.title,
            "start": event.start,
            "end": event.end,
            "resourceIds": [room.slug for room in event.rooms.all()]
            + [person.slug for person in event.people],
        }

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.event_list = self.get_queryset()

        if self.handle_time_constraints_on_get:
            start = self.request.GET.get("start", None)
            end = self.request.GET.get("end", None)

            if start and end is not None:
                self.event_list = self.event_list.filter(
                    Q(start__gte=parser.parse(start)) | Q(end__lte=parser.parse(end))
                )
                # self.event_list = self.event_list.get_in_period(
                #     start=parser.parse(start),
                #     end=parser.parse(end),
                # )

        if self.event_list.model is not Event:
            raise "Event source view mixin requires that the QuerySet is of the model Event"

        events = [
            self.convert_event_to_fc_event(event) for event in self.event_list.all()
        ]

        return JsonResponse(events, safe=False)


class MyCalendarEventsSourceView(EventSourceViewMixin):
    model = Event

    def get_queryset(self):
        user = self.request.user

        if user.person is None:
            raise UserHasNoPersonException(
                "Can not get events for a user that has no person associated with it!"
            )

        return user.person.my_events_qs


my_calendar_events_source_view = MyCalendarEventsSourceView.as_view()


class GetAvailabilityForLocation(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        location_slug = self.request.GET.get("location", None)
        location = Location.objects.get(slug=location_slug)

        result: dict = {}

        now = datetime.datetime.now()

        rooms = location.rooms.all()
        for room in rooms:
            result[room.slug] = (
                Event.objects.filter(
                    Q(rooms__in=[room], start__lte=now, end__gte=now)
                ).count()
                == 0
            )

        return JsonResponse(result, safe=False)


get_availability_for_location_view = GetAvailabilityForLocation.as_view()


class RoomEventSourceView(EventSourceViewMixin):
    model = Event

    def run_raw_query(self, start, end, room_id) -> List[dict]:
        result: List[dict] = []

        query = """
            SELECT
                ev.id,
                ev.title,
                ev.start,
                ev.end,
                arr.id as arrangement_id
                FROM arrangement_event_rooms as aer
                LEFT JOIN arrangement_event as ev on ev.id = aer.event_id
                LEFT JOIN arrangement_arrangement as arr on arr.id = ev.arrangement_id
                WHERE aer.room_id = %s AND ev.start > %s AND ev.end < %s AND ev.is_archived = false AND arr.is_archived = false
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [room_id, start, end])

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))

        return result

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        room_slug = kwargs.get("slug", None)
        room_id = Room.objects.get(slug=room_slug).id
        start = self.request.GET.get("start", None)
        end = self.request.GET.get("end", None)

        events = self.run_raw_query(start, end, room_id)

        return JsonResponse(events, safe=False)


class LocationEventSourceView(EventSourceViewMixin):
    model = Event

    def run_raw_query(self, start, end, location_id) -> List[dict]:
        results: List[dict] = []

        query = """SELECT 
                    ev.id,
                    ev.title, 
                    ev.start, 
                    ev.end, 
                    (array_to_string(array_agg(DISTINCT room.slug ), ',')) as room_slugs,
                    arr.id as arrangement_id 
                    FROM arrangement_arrangement as arr
                    LEFT JOIN arrangement_event as ev on ev.arrangement_id = arr.id
                    LEFT JOIN arrangement_event_rooms as evr on evr.event_id = ev.id
                    LEFT JOIN arrangement_room as room on room.id = evr.room_id
                    WHERE arr.location_id = %s AND ev.is_archived = false AND arr.is_archived = false and ev.start > %s AND ev.end < %s
                    GROUP by ev.id, ev.title, ev.start, ev.end, arr.id"""

        with connection.cursor() as cursor:
            cursor.execute(query, [location_id, start, end])

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                ev = dict(zip(columns, row))
                ev["resourceIds"] = (
                    ev["room_slugs"].split(",") if ev["room_slugs"] else []
                )
                results.append(ev)

        return results

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        location_slug = self.request.GET.get("location", None)
        location_id = Location.objects.get(slug=location_slug).id
        start = self.request.GET.get("start", None)
        end = self.request.GET.get("end", None)

        events = self.run_raw_query(start, end, location_id)

        return JsonResponse(events, safe=False)


location_event_source_view = LocationEventSourceView.as_view()


class CalendarSamplesOverview(
    LoginRequiredMixin, CalendarSectionManifestMixin, MetaMixin, TemplateView
):
    template_name = "arrangement/calendar/calendars_list.html"
    view_meta = ViewMeta(
        subtitle=_("Calendar Samples"), current_crumb_title=_("Calendar Samples")
    )


calendar_samples_overview = CalendarSamplesOverview.as_view()


class ArrangementCalendarView(
    LoginRequiredMixin, CalendarSectionManifestMixin, MetaMixin, TemplateView
):
    template_name = "arrangement/calendar/arrangement_calendar.html"
    view_meta = ViewMeta(
        subtitle=_("Arrangement Calendar"),
        current_crumb_title=_("Arrangement Calendar"),
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["locations"] = Location.objects.all()
        context["people"] = Person.objects.all()
        return context


arrangement_calendar_view = ArrangementCalendarView.as_view()


class DrillCalendarView(
    LoginRequiredMixin, CalendarSectionManifestMixin, MetaMixin, TemplateView
):
    template_name = "arrangement/calendar/drill_calendar.html"
    view_meta = ViewMeta(
        subtitle=_("Drill Calendar"), current_crumb_title=_("Drill Calendar")
    )


drill_calendar_view = DrillCalendarView.as_view()
