# Arrangement Views

# Example:
#from .arrangement_views import (
#   arrangement_create_view
#)

from .location_views import (
    location_detail_view,
    location_update_view,
    location_list_view,
    location_create_view,
    location_delete_view,
)

from .room_views import (
    room_detail_view,
    room_update_view,
    room_list_view,
    room_create_view,
    room_delete_view,
    search_room_ajax_view,
    location_room_list_view,
    search_rooms_ajax_view,
)

from .organization_views import (
    organization_detail_view,
    organization_update_view,
    organization_list_view,
    organization_create_view,
    organization_delete_view,
)

from .person_views import (
    person_detail_view,
    person_update_view,
    person_list_view,
    person_create_view,
    person_delete_view,
    organization_person_member_list_view,
    search_people_ajax_view,
)

from .servicetype_views import (
    service_type_detail_view,
    service_type_update_view,
    service_type_list_view,
    service_type_create_view,
    service_type_delete_view,
    search_service_types,
)

from .organizationtype_views import (
    organization_type_detail_view,
    organization_type_update_view,
    organization_type_list_view,
    organization_type_create_view,
    organization_type_delete_view,
)

from .insights_views import (
    global_timeline_view,
)

from .calendar_views import (
    arrangement_calendar_view,
    calendar_samples_overview,
)

from .arrangement_views import (
    arrangement_detail_view,
    arrangement_create_view,
    arrangement_list_view,
    arrangement_update_view,
    arrangement_delete_view,
    planners_on_arrangement_view,
    planners_on_arrangement_table_view,
    arrangement_add_planner_form_view,
    arrangement_remove_planner_form_view,
    arrangement_promote_planner_to_main_view
)

from .audience_views import (
    audience_detail_view,
    audience_create_view,
    audience_list_view,
    audience_update_view,
    audience_delete_view,
    audience_search_view,
)

from .dashboard_views import (
    dashboard_view,
)

from .planner_views import (
    plan_arrangement_view,
    plan_create_event,
    plan_get_events,
    plan_update_event,
    plan_delete_event,
    plan_delete_events,
    planner_view,
    plan_order_service_view,
    plan_create_events,
)

from .note_views import (
    notes_on_entity_view,
    post_note_view,
    delete_note_view,
    get_notes_view,
)

from .requisition_views import (
    requisition_dashboard_view,
    requisitions_on_event_component_view,
    requisitions_on_arrangement_component_view,
    remove_event_from_requisition_view,
    delete_requisition_view,
)