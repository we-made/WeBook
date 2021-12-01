from django.urls import path

#from webook.arrangement.views import (
#)

from webook.arrangement.views import (
    location_list_view,
    location_detail_view,
    location_update_view,
    location_create_view,
    location_delete_view,

    room_list_view,
    room_detail_view,
    room_update_view,
    room_create_view,
    room_delete_view,

    organization_list_view,
    organization_detail_view,
    organization_update_view,
    organization_create_view,
    organization_delete_view,

    person_list_view,
    person_detail_view,
    person_update_view,
    person_create_view,
    person_delete_view,
)

app_name = "arrangement"
urlpatterns = [
    # Section: arrangement
    # Section: location
    path(
        route="location/list/",
        view=location_list_view,
        name="location_list",
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
        name="location_delete"
    ),
    
    # Section: room
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

    # Section: calendar
    # Section: organization
    path(
        route="organization/list/",
        view=organization_list_view,
        name="organization_list",
    ),
    path(
        route="organization/create/",
        view=organization_create_view,
        name="organization_create",
    ),
    path(
        route="organization/edit/<slug:slug>",
        view=organization_update_view,
        name="organization_edit",
    ),
    path(
        route="organization/<slug:slug>/",
        view=organization_detail_view,
        name="organization_detail",
    ),
    path(
        route="organization/delete/<slug:slug>/",
        view=organization_delete_view,
        name="organization_delete"
    ),

    # Section: person
    path(
        route="person/list/",
        view=person_list_view,
        name="person_list"
    ),

    path(
        route="person/create/",
        view=person_create_view,
        name="person_create",
    ),

    path(
        route="person/edit/<slug:slug>",
        view=person_update_view,
        name="person_edit"
    ),

    path(
        route="person/<slug:slug>/",
        view=person_detail_view,
        name="person_detail",
    ),

    path(
        route="person/delete/<slug:slug>/",
        view=person_delete_view,
        name="person_delete",
    )
]