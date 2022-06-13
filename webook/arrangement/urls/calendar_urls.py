from django.urls import path
from webook.arrangement.views import (
    calendar_samples_overview,
    arrangement_calendar_view,
    drill_calendar_view,
    my_calendar_events_source_view,
    all_locations_resource_source_view,
    all_people_resource_source_view,
    all_rooms_resource_source_view,
)


calendar_urls = [
    path(
        route="calendar/sample_overview",
        view=calendar_samples_overview,
        name="sample_overview",
    ),
    path(
        route="calendar/arrangement_calendar",
        view=arrangement_calendar_view,
        name="arrangement_calendar",
    ),
    path(
        route="calendar/drill_calendar",
        view=drill_calendar_view,
        name="drill_calendar",
    ),
    path(
        route="calendar/sources/my_events",
        view=my_calendar_events_source_view,
        name="my_events_event_source",
    ),
    path(
        route="calendar/resources/all_rooms",
        view=all_rooms_resource_source_view,
        name="all_rooms_resource_source",
    ),
    path(
        route="calendar/resources/all_people",
        view=all_people_resource_source_view,
        name="all_people_resource_source",
    ),
    path(
        route="calendar/resources/all_locations",
        view=all_locations_resource_source_view,
        name="all_locations_resource_source",
    ),
]