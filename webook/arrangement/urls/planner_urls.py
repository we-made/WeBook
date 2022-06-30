from unicodedata import name

from django.urls import path

from webook.arrangement import views
from webook.arrangement.views import (
    arrangement_add_planner_dialog_view,
    arrangement_add_planners_form_view,
    arrangement_calendar_planner_dialog_view,
    arrangement_create_serie_dialog_view,
    arrangement_create_simple_event_dialog_view,
    arrangement_information_dialog_view,
    arrangement_new_note_dialog_view,
    arrangement_promote_planner_dialog_view,
    arrangement_remove_planners_form_view,
    create_arrangement_dialog_view,
    get_arrangements_in_period_view,
    get_collision_analysis_view,
    plan_arrangement_view,
    plan_create_event,
    plan_delete_events,
    plan_get_events,
    plan_get_loose_service_requisitions,
    plan_loose_service_requisitions_component_view,
    plan_order_service_view,
    plan_people_requisitions_component_view,
    plan_people_to_requisition_component_view,
    planner_arrangement_events_view,
    planner_calendar_filter_rooms_dialog_view,
    planner_calendar_order_people_for_event_form_view,
    planner_calendar_order_person_dialog_view,
    planner_calendar_order_person_for_series_form_view,
    planner_calendar_order_room_dialog_view,
    planner_calendar_order_room_for_event_form_view,
    planner_calendar_order_rooms_for_series_form_view,
    planner_calendar_remove_person_from_event_form_view,
    planner_calendar_remove_room_from_event_form_view,
    planner_calendar_upload_file_to_arrangement_dialog_view,
    planner_calendar_upload_file_to_event_serie_dialog_view,
    planner_calendar_view,
    planner_event_inspector_dialog_view,
    planner_view,
    upload_files_dialog,
)

planner_urls = [
    path(
        route="planner/planner",
        view=planner_view,
        name="planner",
    ),
    path(
        route="planner/plan",
        view=plan_arrangement_view,
        name="plan_arrangement"
    ),
    path(
        route="planner/create_event",
        view=plan_create_event,
        name="plan_create_event"
    ),
    path(
        route="planner/get_events",
        view=plan_get_events,
        name="plan_get_events",
    ),
    path(
        route="planner/delete_events/",
        view=plan_delete_events,
        name="plan_delete_events",
    ),
    path(
        route="planner/order_service/",
        view=plan_order_service_view,
        name="plan_order_service",
    ),
    path(
        route="planner/get_collision_analysis/",
        view=get_collision_analysis_view,
        name="get_collision_analysis",
    ),
    path(
        route="planner/loose_service_requisitions",
        view=plan_get_loose_service_requisitions,
        name="get_loose_service_requisitions",
    ),
    path(
        route="planner/loose_service_requisitions_table",
        view=plan_loose_service_requisitions_component_view,
        name="loose_service_requisitions_table_component",
    ),
    path(
        route="planner/people_requisitions_table",
        view=plan_people_requisitions_component_view,
        name="people_requisitions_table_component",
    ),
    path(
        route="planner/people_to_requisition_table",
        view=plan_people_to_requisition_component_view,
        name="people_to_requisition_table_component"
    ),
    path(
        route="planner/calendar",
        view=planner_calendar_view,
        name="planner_calendar",
    ),
    path(
        route="planner/arrangements_as_events",
        view=planner_arrangement_events_view,
        name="arrangement_events",
    ),
    path(
        route="planner/arrangements_in_period",
        view=get_arrangements_in_period_view,
        name="arrangements_in_period"
    ),
    path(
        route="planner/dialogs/arrangement_information/<slug:slug>",
        view=arrangement_information_dialog_view,
        name="arrangement_dialog",
    ),
    path(
        route="planner/dialogs/arrangement_calendar_planner/<slug:slug>",
        view=arrangement_calendar_planner_dialog_view,
        name="arrangement_planner_dialog",
    ),
    path(
        route="planner/dialogs/create_simple_event",
        view=arrangement_create_simple_event_dialog_view,
        name="arrangement_create_event_dialog"
    ),
    path(
        route="planner/dialogs/create_serie",
        view=arrangement_create_serie_dialog_view,
        name="arrangement_create_serie_dialog",
    ),
    path(
        route="planner/dialogs/promote_main_planner",
        view=arrangement_promote_planner_dialog_view,
        name="arrangement_promote_main_planner_dialog",
    ),
    path(
        route="planner/dialogs/new_note",
        view=arrangement_new_note_dialog_view,
        name="arrangement_new_note_dialog",
    ),
    path(
        route="planner/dialogs/add_planner",
        view=arrangement_add_planner_dialog_view,
        name="arrangement_add_planner_dialog",
    ),
    path(
        route="planner/add_planners",
        view=arrangement_add_planners_form_view,
        name="arrangement_add_planners_form",
    ),
    path(
        route="planner/remove_planners",
        view=arrangement_remove_planners_form_view,
        name="arrangement_remove_planners_form"
    ),
    path(
        route="planner/dialogs/create_arrangement",
        view=create_arrangement_dialog_view,
        name="create_arrangement_dialog"
    ),
    path(
        route="planner/dialogs/event_inspector/<int:pk>",
        view=planner_event_inspector_dialog_view,
        name="event_inspector_dialog",
    ),
    path(
        route="planner/dialogs/room_filter",
        view=planner_calendar_filter_rooms_dialog_view,
        name="filter_room_dialog",
    ),
    path(
        route="planner/dialogs/order_person",
        view=planner_calendar_order_person_dialog_view,
        name="order_person_dialog",
    ),
    path(
        route="planner/dialogs/order_room",
        view=planner_calendar_order_room_dialog_view,
        name="order_room_dialog",
    ),
    path(
        route="planner/dialogs/order_people_form",
        view=planner_calendar_order_person_for_series_form_view,
        name="order_people_form"
    ),
    path(
        route="planner/dialogs/order_rooms_form",
        view=planner_calendar_order_rooms_for_series_form_view,
        name="order_rooms_form",
    ),
    path(
        route="planner/dialogs/order_rooms_for_event_form",
        view = planner_calendar_order_room_for_event_form_view,
        name="order_room_for_event_form"
    ),
    path(
        route="planner/dialogs/order_people_for_event_form",
        view=planner_calendar_order_people_for_event_form_view,
        name="order_people_for_event_form",
    ),
    path(
        route="planner/remove_person_from_event",
        view=planner_calendar_remove_person_from_event_form_view,
        name="remove_person_from_event"
    ),
    path(
        route="planner/remove_room_from_event",
        view=planner_calendar_remove_room_from_event_form_view,
        name="remove_room_from_event",
    ),
    path(
        route="planner/dialogs/upload_files_to_arrangement",
        view=planner_calendar_upload_file_to_arrangement_dialog_view,
        name="upload_files_to_arrangement"
    ),
    path(
        route="planner/dialogs/upload_files_to_event_serie",
        view=planner_calendar_upload_file_to_event_serie_dialog_view,
        name="upload_files_to_event_serie"
    ),
    path(
        route="planner/dialogs/upload_files_dialog",
        view=upload_files_dialog,
        name="upload_files_dialog",
    ),
]
