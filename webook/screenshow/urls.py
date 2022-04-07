from django.urls import path
from webook.screenshow.views.views import (
    layout_list_view,
    layout_create_view,
    layout_detail_view,
    layout_update_view,
    layout_delete_view,
)

app_name = "screenshow"


urlpatterns = [
    path("layout/list/", view=layout_list_view, name="layout_list"),
    path("layout/create/", view=layout_create_view, name="layout_create"),
    path("layout/<slug:slug>/", view=layout_detail_view, name="layout_detail"),
    path("layout/edit/<slug:slug>/", view=layout_update_view, name="layout_edit"),
    path("layout/delete/<slug:slug>/", view=layout_delete_view, name="layout_delete"),
]
