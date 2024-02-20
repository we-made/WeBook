from unicodedata import name

from django.urls import path

from webook.arrangement.views.room_views import *

room_urls = [
    path(
        route="room/list/",
        view=room_list_view,
        name="room_list",
    ),
    path(
        route="room/create/",
        view=room_create_view,
        name="room_create",
    ),
    path(
        route="room/edit/<slug:slug>",
        view=room_update_view,
        name="room_edit",
    ),
    path(
        route="room/<slug:slug>/",
        view=room_detail_view,
        name="room_detail",
    ),
    path(
        route="room/delete/<slug:slug>/",
        view=room_delete_view,
        name="room_delete",
    ),
    path(
        route="room/locationrooms?location=<str:location>",
        view=location_room_list_view,
        name="locationroomlist",
    ),
    path(
        route="room/search",
        view=search_rooms_ajax_view,
        name="search_room_ajax_view",
    ),
    path(
        route="room/json/<slug:slug>/",
        view=room_detail_json_view,
        name="room_detail_json_view",
    ),
    path(
        route="room/create/json/",
        view=room_create_json_view,
        name="room_create_json_view",
    ),
    path(
        route="room/update/json/<slug:slug>/",
        view=room_update_json_view,
        name="room_update_json_view",
    ),
    path(
        route="room/select2/json/",
        view=rooms_select2_json_view,
        name="rooms_select2_json_view",  
    ),
]
