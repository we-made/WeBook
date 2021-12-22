from django.urls import path


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
    location_room_list_view,

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
    organization_person_member_list_view,

    service_type_list_view,
    service_type_detail_view,
    service_type_update_view,
    service_type_create_view,
    service_type_delete_view,

    organization_type_list_view,
    organization_type_detail_view,
    organization_type_update_view,
    organization_type_create_view,
    organization_type_delete_view,

    arrangement_calendar_view,
    calendar_samples_overview,

    arrangement_list_view,
    arrangement_detail_view,
    arrangement_update_view,
    arrangement_create_view,
    arrangement_delete_view,

    audience_list_view,
    audience_detail_view,
    audience_update_view,
    audience_create_view,
    audience_delete_view,

    dashboard_view,

    global_timeline_view,
)

app_name = "arrangement"
urlpatterns = [
    # Section: arrangement

    path(
        route="arrangement/list/",
        view=arrangement_list_view,
        name="arrangement_list",
    ),
    path(
        route="arrangement/create/",
        view=arrangement_create_view,
        name="arrangement_create",
    ),
    path(
        route="arrangement/edit/<slug:slug>",
        view=arrangement_update_view,
        name="arrangement_edit",
    ),
    path(
        route="arrangement/<slug:slug>/",
        view=arrangement_detail_view,
        name="arrangement_detail",
    ),
    path(
        route="arrangement/delete/<slug:slug>",
        view=arrangement_delete_view,
        name="arrangement_delete",
    ),

    path(
        route="audience/list/",
        view = audience_list_view,
        name="audience_list"
    ),
    path(
        route="audience/create/",
        view=audience_create_view,
        name="audience_create",
    ),
    path(
        route="audience/edit/<slug:slug>",
        view=audience_update_view,
        name="audience_edit",
    ),
    path(
        route="audience/<slug:slug>/",
        view=audience_detail_view,
        name="audience_detail",
    ),
    path(
        route="audience/delete/<slug:slug>",
        view=audience_delete_view,
        name="audience_delete",
    ),


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
        route="insights/globaltimeline",
        view=global_timeline_view,
        name="global_timeline"
    ),

    #Section: organization type
    path(
        route="organizationtype/list/",
        view=organization_type_list_view,
        name="organizationtype_list",
    ),
    path(
        route="organizationtype/create/",
        view=organization_type_create_view,
        name="organizationtype_create",
    ),
    path(
        route="organizationtype/edit/<slug:slug>",
        view=organization_type_update_view,
        name="organizationtype_edit",
    ),
    path(
        route="organizationtype/<slug:slug>/",
        view=organization_type_detail_view,
        name="organizationtype_detail",
    ),
    path(
        route="organizationtype/delete/<slug:slug>",
        view=organization_type_delete_view,
        name="organizationtype_delete",
    ),

    #Section: service type
    path(
        route="servicetype/list/",
        view=service_type_list_view,
        name="servicetype_list",
    ),
    path(
        route="servicetype/create/",
        view=service_type_create_view,
        name="servicetype_create",
    ),
    path(
        route="servicetype/edit/<slug:slug>",
        view=service_type_update_view,
        name="servicetype_edit",
    ),
    path(
        route="servicetype/<slug:slug>/",
        view=service_type_detail_view,
        name="servicetype_detail",
    ),
    path(
        route="servicetype/delete/<slug:slug>",
        view=service_type_delete_view,
        name="servicetype_delete",
    ),

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

    path(
        route="room/locationrooms?location=<str:location>",
        view=location_room_list_view, 
        name="locationroomlist"
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

    path(
        route="person/organizationmemberlist?organization=<str:organization>",
        view=organization_person_member_list_view,
        name="organizationmemberlist"
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
    ),

    path(
        route="dashboard",
        view=dashboard_view,
        name="dashboard"
    ),
]