from django.urls import path

from webook.users.views import (
    batch_deactivate_users_view,
    sso_detail_dialog_view,
    toggle_user_active_state_view,
    user_admin_detail_dialog_view,
    user_detail_view,
    user_redirect_view,
    user_update_view,
    users_json_list_view,
    users_list_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<slug:slug>/", view=user_detail_view, name="detail"),
    path("administration/list", view=users_list_view, name="user_admin_list"),
    path("administration/json_list", view=users_json_list_view, name="users_json_list"),
    path(
        "administration/<slug:slug>/dialogs/sso_detail",
        view=sso_detail_dialog_view,
        name="user_admin_sso_detail",
    ),
    path(
        "administration/<slug:slug>/dialogs/user_admin_detail",
        view=user_admin_detail_dialog_view,
        name="user_admin_detail",
    ),
    path(
        "administration/batch_deactivate_users",
        view=batch_deactivate_users_view,
        name="user_admin_batch_deactivate",
    ),
    path(
        "administration/toggle_active",
        view=toggle_user_active_state_view,
        name="user_admin_toggle_active",
    ),
]
