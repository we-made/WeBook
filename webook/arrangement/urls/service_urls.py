from unicodedata import name

from django.urls import path

from webook.arrangement.views import (
    create_service_template_view,
    create_service_view,
    delete_service_email_from_service_view,
    process_service_request_view,
    services_add_email_view,
    services_add_person_view,
    services_dashboard_view,
    services_json_list_view,
    toggle_service_active_json_view,
    update_service_view,
)

service_urls = [
    path(
        route="service/dashboard",
        view=services_dashboard_view,
        name="services_dashboard",
    ),
    path(
        route="service/json/list",
        view=services_json_list_view,
        name="services_json_list",
    ),
    path(
        route="service/add_email/<int:pk>",
        view=services_add_email_view,
        name="services_add_email",
    ),
    path(
        route="service/add_person/<int:pk>",
        view=services_add_person_view,
        name="services_add_person",
    ),
    path(
        route="service/<int:id>/toggle",
        view=toggle_service_active_json_view,
        name="service_deactivate",
    ),
    path(
        route="service/create",
        view=create_service_view,
        name="services_create",
    ),
    path(
        route="service/<int:pk>/update",
        view=update_service_view,
        name="services_update",
    ),
    path(
        route="service/delete_email",
        view=delete_service_email_from_service_view,
        name="service_delete_email",
    ),
    path(
        route="service/create_template",
        view=create_service_template_view,
        name="create_service_template",
    ),
    path(
        route="/service/process/<str:token>",
        view=process_service_request_view,
        name="process_service_order",
    ),
]
