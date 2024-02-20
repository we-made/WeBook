from django.urls import path

from webook.arrangement.views.room_preset_views import *

room_preset_urls = [
    path(
        name="room_preset_list",
        route="room_preset/list",
        view=room_presets_listview,
    ),
    path(
        name="room_preset_update",
        route="room_preset/edit/<slug:slug>",
        view=room_preset_update_view,
    ),
    path(
        name="room_preset_create",
        route="room_preset/create",
        view=room_preset_create_view,
    ),
    path(
        name="room_preset_delete",
        route="room_preset/delete/<slug:slug>",
        view=room_preset_delete_view,
    ),
    path(
        name="room_preset_json_list_view",
        route="room_preset/json_list",
        view=room_preset_json_list_view,
    ),
    path(
        name="room_preset_detail",
        route="room_preset/<slug:slug>",
        view=room_preset_detail_view,
    ),
]
