from django.urls import path
from webook.arrangement.views import (
    person_list_view,
    person_create_view,
    person_update_view,
    person_detail_view,
    person_delete_view,
)


person_urls = [
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
]