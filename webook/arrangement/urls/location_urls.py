from django.urls import path

from webook.arrangement.views import (
    location_create_view,
    location_delete_view,
    location_detail_view,
    location_list_view,
    location_rooms_json_list_view,
    location_update_view,
    locations_calendar_resources_list_view,
    locations_tree_json_view,
)

location_urls = [
    path(
        route="location/list/",
        view=location_list_view,
        name="location_list",
    ),
    path(
        route="location/tree/",
        view=locations_tree_json_view,
        name="location_tree",
    ),
    path(
        route="location/create/",
        view=location_create_view,
        name="location_create",
    ),
    path(
        route="location/edit/<slug:slug>",
        view=location_update_view,
        name="location_edit",
    ),
    path(
        route="location/<slug:slug>/",
        view=location_detail_view,
        name="location_detail",
    ),
    path(
        route="location/delete/<slug:slug>/",
        view=location_delete_view,
        name="location_delete",
    ),
    path(
        route="location/calendar_resources",
        view=locations_calendar_resources_list_view,
        name="location_calendar_resources",
    ),
    path(
        route="location/location_rooms_json/<slug:slug>",
        view=location_rooms_json_list_view,
        name="location_rooms_json",
    ),
]
