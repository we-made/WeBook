from django.urls import path

from webook.arrangement.views import (
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
from webook.arrangement.views.event_views import (
    GetEventJsonView,
    get_event_popover_json_view,
)

event_urls = [ 
    path(
        route="event/<int:pk>/popover_json",
        view=get_event_popover_json_view,
        name="get_event_json",
    ),
    path(
        route="event/<int:pk>/json",
        view=GetEventJsonView.as_view(),
        name="get_event_json",
    ),
    path(
        route="event/create_serie",
        view=create_event_serie_json_view,
        name="create_event_serie",
    ),
    path(
        route="event/create",
        view=create_event_json_view,
        name="create_event",
    ),
    path(
        route="event/<int:pk>/upload",
        view=upload_files_to_event_json_form_view,
        name="upload_files_to_event",
    ),
    path(
        route="event/<int:event_pk>/files/<int:pk>/delete",
        view=delete_file_from_event_view,
        name="delete_file_from_event",
    ),
    path(
        route="planner/update_event/<int:pk>",
        view=update_event_json_view,
        name="plan_update_event",
    ),
    path(
        route="planner/delete_event/<int:pk>",
        view=delete_event_json_view,
        name="plan_delete_event",
    ),
    path(
        route="eventSerie/files/delete/<int:pk>",
        view=event_serie_delete_file_view,
        name="event_serie_delete_file",
    ),
    path(
        route="eventSerie/<int:pk>/files/upload",
        view=upload_files_to_event_serie_json_form_view,
        name="upload_files_to_event_serie",
    ),
    path(
        route="eventSerie/delete/<int:pk>",
        view=delete_event_serie_view,
        name="delete_event_serie",
    ),
    path(
        route="eventSerie/<int:pk>/manifest",
        view=event_serie_manifest_view,
        name="event_serie_manifest",
    ),
    path(
        route="eventSerie/<int:pk>/calculate",
        view=calculate_event_serie_view,
        name="calculate_event_serie",
    ),
    path(
        route="eventSerie/<int:pk>/preview",
        view=calculate_event_serie_preview_view,
        name="calculate_event_serie_preview",
    ),
]
