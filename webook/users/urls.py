from django.urls import path

from webook.users.views import (
    ClearProfilePictureView,
    batch_change_user_group_view,
    batch_change_user_state_view,
    clear_profile_picture_view,
    sso_detail_dialog_view,
    toggle_user_active_state_view,
    toggle_user_admin_state_form_view,
    update_profile_picture_view,
    update_user_details_form_view,
    update_user_role_form_view,
    user_admin_detail_dialog_view,
    user_by_email_exists_json_view,
    user_detail_json_view,
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
        "administration/<slug:slug>/update_profile_picture",
        view=update_profile_picture_view,
        name="update_profile_picture",
    ),
    path(
        "administration/<slug:slug>/clear_profile_picture",
        view=clear_profile_picture_view,
        name="clear_profile_picture_view",
    ),
    path(
        "administration/<slug:slug>/update_details",
        view=update_user_details_form_view,
        name="update_user_details",
    ),
    path(
        "administration/<slug:slug>/toggle_active",
        view=toggle_user_active_state_view,
        name="toggle_active",
    ),
    path(
        "administration/<slug:slug>/toggle_user_admin",
        view=toggle_user_admin_state_form_view,
        name="toggle_user_admin",
    ),
    path(
        "administration/<slug:slug>/update_role",
        view=update_user_role_form_view,
        name="update_user_role",
    ),
    path(
        "administration/json_detail/<slug:slug>",
        view=user_detail_json_view,
        name="user_json_detail",
    ),
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
