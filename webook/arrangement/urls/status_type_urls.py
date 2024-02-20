from django.urls import path

from webook.arrangement.views.status_type_views import *

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
    path(
        route="statustype/tree", view=status_type_tree_json_view, name="statustype_tree"
    ),
]
