from django.urls import path
from webook.arrangement.views import (
    event_serie_delete_file_view,
    delete_event_serie_view,
    event_serie_manifest_view,
)


event_serie_urls = [
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
    )
]