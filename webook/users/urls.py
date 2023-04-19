from django.urls import path

from webook.users.views import (
    batch_change_user_group_view,
    batch_change_user_state_view,
    sso_detail_dialog_view,
    toggle_user_active_state_view,
    user_admin_detail_dialog_view,
    user_by_email_exists_json_view,
    user_detail_view,
    user_redirect_view,
    user_update_view,
    users_json_list_view,
    users_list_view,
)

app_name = "users"
urlpatterns = [
    path("exists/", view=user_by_email_exists_json_view, name="exists_by_mail"),
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
        "administration/batch_change_user_state",
        view=batch_change_user_state_view,
        name="user_admin_batch_change_active_state",
    ),
    path(
        "administration/batch_change_user_group_view",
        view=batch_change_user_group_view,
        name="user_admin_batch_change_group",
    ),
    path(
        "administration/toggle_active",
        view=toggle_user_active_state_view,
        name="user_admin_toggle_active",
    ),
]
