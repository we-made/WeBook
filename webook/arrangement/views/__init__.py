# Arrangement Views

# Example:
# from .arrangement_views import (
#   arrangement_create_view
# )


from .analysis_views import (
    analyze_arrangement_view,
    analyze_non_existant_event_view,
    analyze_non_existent_serie_manifest_view,
)
from .arrangement_views import (
    arrangement_add_planner_form_view,
    arrangement_cascade_tree_dialog_view,
    arrangement_cascade_tree_json_view,
    arrangement_create_json_view,
    arrangement_create_view,
    arrangement_delete_file_view,
    arrangement_delete_view,
    arrangement_promote_planner_to_main_view,
    arrangement_recurring_information_json_view,
    arrangement_remove_planner_form_view,
    arrangement_search_view,
    arrangement_update_view,
    arrangement_upload_files_json_form_view,
    planners_on_arrangement_table_view,
    planners_on_arrangement_view,
    synchronize_events_in_arrangement_view,
)
from .arrangementtype_views import (
    arrangement_type_create_view,
    arrangement_type_delete_view,
    arrangement_type_detail_view,
    arrangement_type_list_view,
    arrangement_type_tree_json_view,
    arrangement_type_update_view,
)
from .audience_views import (
    audience_create_view,
    audience_delete_view,
    audience_detail_view,
    audience_list_view,
    audience_search_view,
    audience_tree_json_view,
    audience_update_view,
)
from .calendar_views import (
    all_locations_resource_source_view,
    all_people_resource_source_view,
    all_rooms_resource_source_view,
    arrangement_calendar_view,
    calendar_samples_overview,
    drill_calendar_view,
    location_event_source_view,
    my_calendar_events_source_view,
    rooms_on_location_resource_source_view,
)
from .confirmation_views import (
    confirmation_request_accept_view,
    confirmation_request_deny_view,
    thanks_after_response_view,
    view_confirmation_request_view,
)
from .event_views import (
    calculate_event_serie_preview_view,
    calculate_event_serie_view,
    create_event_json_view,
    create_event_serie_json_view,
    delete_event_json_view,
    delete_event_serie_view,
    delete_file_from_event_view,
    event_serie_delete_file_view,
    event_serie_manifest_view,
    update_event_json_view,
    upload_files_to_event_json_form_view,
    upload_files_to_event_serie_json_form_view,
)
from .location_views import (
    location_create_view,
    location_delete_view,
    location_detail_view,
    location_list_view,
    location_update_view,
    locations_calendar_resources_list_view,
    locations_tree_json_view,
)
from .note_views import (
    delete_note_view,
    get_notes_view,
    notes_on_entity_view,
    post_note_view,
)
from .notification_views import (
    archive_notification_view,
    marK_all_notifications_as_seen_view,
    mark_notification_as_seen_view,
    my_notifications_json_list_view,
)
from .organization_views import (
    organization_create_view,
    organization_delete_view,
    organization_detail_view,
    organization_list_view,
    organization_register_service_providable_form_view,
    organization_services_providable_view,
    organization_update_view,
)
from .organizationtype_views import (
    organization_type_create_view,
    organization_type_delete_view,
    organization_type_detail_view,
    organization_type_list_view,
    organization_type_update_view,
)
from .person_views import (
    associate_person_with_user_form_view,
    organization_person_member_list_view,
    people_calendar_resources_list_view,
    person_create_view,
    person_delete_view,
    person_detail_view,
    person_list_view,
    person_update_view,
    search_people_ajax_view,
)
from .planner_views import (
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
    inspect_service_order_dialog_view,
    order_service_dialog_view,
    plan_arrangement_view,
    plan_create_event,
    plan_delete_events,
    plan_get_events,
    plan_get_loose_service_requisitions,
    plan_loose_service_requisitions_component_view,
    plan_order_service_view,
    plan_people_requisitions_component_view,
    plan_people_to_requisition_component_view,
    planner_arrangement_edit_note_dialog_view,
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
    planner_calendar_view,
    planner_event_inspector_dialog_view,
    planner_view,
    upload_files_dialog,
)
from .requisition_views import (
    cancel_service_requisition_form_view,
    delete_requisition_view,
    delete_service_requisition_view,
    remove_event_from_requisition_view,
    requisition_dashboard_view,
    requisition_person_form_view,
    requisition_service_form_view,
    requisitions_on_arrangement_component_view,
    requisitions_on_event_component_view,
    reset_requisition_form_view,
)
from .room_preset_views import (
    room_preset_create_view,
    room_preset_delete_view,
    room_preset_detail_view,
    room_preset_update_view,
    room_presets_listview,
)
from .room_views import (
    location_room_list_view,
    room_create_view,
    room_delete_view,
    room_detail_view,
    room_list_view,
    room_update_view,
    search_room_ajax_view,
    search_rooms_ajax_view,
)
from .service_views import (
    archive_preconfiguration_json_view,
    cancel_service_order_form_view,
    confirm_service_order_form_view,
    create_change_log_note_view,
    create_preconfiguration_json_view,
    create_service_template_view,
    create_service_view,
    delete_service_email_from_service_view,
    deny_service_order_form_view,
    get_change_summary_json_view,
    get_events_for_resource_in_sopr_json_view,
    get_personell_json_view,
    get_preconfigurations_for_service_json_view,
    get_provisions_json_view,
    get_service_overview_calendar,
    get_service_responsibles_json_view,
    open_service_order_for_revisioning_form_view,
    process_service_request_view,
    provision_personell_form_view,
    redirect_to_process_service_request_view,
    service_detail_view,
    service_order_dashboard,
    service_orders_for_service_json_list_view,
    service_personnell_json_list_view,
    services_add_email_view,
    services_add_person_view,
    services_dashboard_view,
    services_json_list_view,
    toggle_service_active_json_view,
    update_preconfiguration_json_view,
    update_service_view,
)
from .servicetype_views import (
    search_service_types,
    service_type_create_view,
    service_type_delete_view,
    service_type_detail_view,
    service_type_list_view,
    service_type_update_view,
)
from .status_type_views import (
    status_type_create_view,
    status_type_delete_view,
    status_type_list_view,
    status_type_tree_json_view,
    status_type_update_view,
)
