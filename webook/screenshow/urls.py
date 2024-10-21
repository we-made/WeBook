from django.urls import path
from webook.screenshow.views.layout_view import (
    layout_list_view,
    layout_create_view,
    layout_detail_view,
    layout_update_view,
    layout_delete_view,
    layout_list_json_view,
)
from webook.screenshow.views.screen_view import (
    screen_list_view,
    screen_create_view,
    screen_detail_view,
    screen_update_view,
    screen_delete_view,
)
from webook.screenshow.views.group_view import (
    screen_group_list_view,
    screen_group_create_view,
    screen_group_detail_view,
    screen_group_update_view,
    screen_group_delete_view,
)

app_name = "screenshow"


urlpatterns = [
    path("layout/list/", view=layout_list_view, name="layout_list"),
    path("layout/create/", view=layout_create_view, name="layout_create"),
    path("layout/<slug:slug>/", view=layout_detail_view, name="layout_detail"),
    path("layout/edit/<slug:slug>/", view=layout_update_view, name="layout_edit"),
    path("layout/delete/<slug:slug>/", view=layout_delete_view, name="layout_delete"),
    path("layout/list/json", view=layout_list_json_view, name="layout_list_json"),

    path("screen/list/", view=screen_list_view, name="screen_list"),
    path("screen/create/", view=screen_create_view, name="screen_create"),
    path("screen/<slug:slug>/", view=screen_detail_view, name="screen_detail"),
    path("screen/edit/<slug:slug>/", view=screen_update_view, name="screen_edit"),
    path("screen/delete/<slug:slug>/", view=screen_delete_view, name="screen_delete"),

    path("screengroup/list/", view=screen_group_list_view, name="screen_group_list"),
    path("screengroup/create/", view=screen_group_create_view, name="screen_group_create"),
    path("screengroup/<slug:slug>/", view=screen_group_detail_view, name="screen_group_detail"),
    path("screengroup/edit/<slug:slug>/", view=screen_group_update_view, name="screen_group_edit"),
    path("screengroup/delete/<slug:slug>/", view=screen_group_delete_view, name="screen_group_delete"),
]
