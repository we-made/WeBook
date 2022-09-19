from django.urls import path

from webook.arrangement.views import (
    status_type_create_view,
    status_type_delete_view,
    status_type_list_view,
    status_type_update_view,
)

status_type_urls = [
    path(
        route="statustype/list/",
        view=status_type_list_view,
        name="statustype_list",
    ),
    path(
        route="statustype/create/",
        view=status_type_create_view,
        name="statustype_create",
    ),
    path(
        route="statustype/edit/<slug:slug>",
        view=status_type_update_view,
        name="statustype_update",
    ),
    path(
        route="statustype/delete/<slug:slug>",
        view=status_type_delete_view,
        name="statustype_delete",
    ),
]
