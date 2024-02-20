from unicodedata import name

from django.urls import path

from webook.arrangement.views.arrangementtype_views import *

arrangement_type_urls = [
    path(
        route="arrangementtype/list/",
        view = arrangement_type_list_view,
        name="arrangement_type_list"
    ),
    path(
        route="arrangementtype/create/",
        view=arrangement_type_create_view,
        name="arrangement_type_create",
    ),
    path(
        route="arrangementtype/edit/<slug:slug>",
        view=arrangement_type_update_view,
        name="arrangement_type_edit",
    ),
    path(
        route="arrangementtype/<slug:slug>/",
        view=arrangement_type_detail_view,
        name="arrangement_type_detail",
    ),
    path(
        route="arrangementtype/delete/<slug:slug>",
        view=arrangement_type_delete_view,
        name="arrangement_type_delete",
    ),
    path(
        route="arrangementtype/treelist",
        view=arrangement_type_tree_json_view,
        name="arrangement_type_tree_list",
    ),
]
