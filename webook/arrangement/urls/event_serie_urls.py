from unicodedata import name
from django.urls import path
from webook.arrangement import views


from webook.arrangement.views import (
    event_serie_delete_file_view
)


event_serie_urls = [
    path(
        route="eventSerie/files/delete/<int:pk>",
        view=event_serie_delete_file_view,
        name="event_serie_delete_file",
    ),
]