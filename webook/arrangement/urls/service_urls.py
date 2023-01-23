from unicodedata import name

from django.urls import path

from webook.arrangement.views import (
    create_service_view,
    services_add_email_view,
    services_dashboard_view,
    services_json_list_view,
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
        route="service/create",
        view=create_service_view,
        name="services_create",
    ),
    path(route="service/update", view=update_service_view, name="services_update"),
]
