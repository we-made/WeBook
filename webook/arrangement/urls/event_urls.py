from django.urls import path

from webook.arrangement.views import (
    calculate_event_serie_preview_view,
    calculate_event_serie_view,
    create_event_json_view,
    create_event_serie_json_view,
    delete_event_serie_view,
    event_serie_delete_file_view,
    event_serie_manifest_view,
)

event_urls = [
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
        route="eventSerie/files/delete/<int:pk>",
        view=event_serie_delete_file_view,
        name="event_serie_delete_file",
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
