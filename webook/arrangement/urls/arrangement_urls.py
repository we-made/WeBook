from unicodedata import name

from django.urls import path

from webook.arrangement.views import (
    arrangement_add_planner_form_view,
    arrangement_cascade_tree_dialog_view,
    arrangement_cascade_tree_json_view,
    arrangement_create_json_view,
    arrangement_create_view,
    arrangement_delete_file_view,
    arrangement_delete_view,
    arrangement_promote_planner_to_main_view,
    arrangement_recurring_information_json_view,
    arrangement_remove_planner_form_view,
    arrangement_search_view,
    arrangement_update_view,
    arrangement_upload_files_json_form_view,
    planners_on_arrangement_table_view,
    planners_on_arrangement_view,
    synchronize_events_in_arrangement_view,
)

arrangement_urls = [
    path(
        route="arrangement/<int:pk>/detail",
        view=arrangement_recurring_information_json_view,
        name="arrangement_recurring_info_json",
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
        route="arrangement/delete/<slug:slug>",
        view=arrangement_delete_view,
        name="arrangement_delete",
    ),
    path(
        route="arrangement/planners",
        view=planners_on_arrangement_view,
        name="planners_on_arrangement",
    ),
    path(
        route="arrangement/add_planner",
        view=arrangement_add_planner_form_view,
        name="arrangement_add_planner",
    ),
    path(
        route="arrangement/remove_planner",
        view=arrangement_remove_planner_form_view,
        name="arrangement_remove_planner",
    ),
    path(
        route="arrangement/planners_table",
        view=planners_on_arrangement_table_view,
        name="arrangement_planners_table",
    ),
    path(
        route="arrangement/promote_to_main",
        view=arrangement_promote_planner_to_main_view,
        name="arrangement_promote_planner_to_main",
    ),
    path(
        route="arrangement/search",
        view=arrangement_search_view,
        name="arrangement_search",
    ),
    path(
        route="arrangement/ajax/create",
        view=arrangement_create_json_view,
        name="arrangement_ajax_create",
    ),
    path(
        route="arrangement/files/upload",
        view=arrangement_upload_files_json_form_view,
        name="arrangement_file_upload",
    ),
    path(
        route="arrangement/files/delete/<int:pk>",
        view=arrangement_delete_file_view,
        name="arrangement_file_delete",
    ),
    path(
        route="arrangement/<int:pk>/cascade_tree",
        view=arrangement_cascade_tree_json_view,
        name="arrangement_cascade_tree_json",
    ),
    path(
        route="arrangement/<int:pk>/dialogs/cascade_tree",
        view=arrangement_cascade_tree_dialog_view,
        name="arrangement_cascade_tree_dialog",
    ),
    path(
        route="arrangement/synchronize",
        view=synchronize_events_in_arrangement_view,
        name="arrangement_synchronize_events",
    ),
]
