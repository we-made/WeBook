from django.urls import path
from webook.arrangement.views import (
    arrangement_list_view,
    arrangement_create_view,
    arrangement_update_view,
    arrangement_detail_view,
    arrangement_delete_view,
)


arrangement_urls = [
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
]