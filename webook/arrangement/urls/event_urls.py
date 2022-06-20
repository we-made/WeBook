from django.urls import path

from webook.arrangement.views import create_event_json_view, create_event_serie_json_view

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
]
