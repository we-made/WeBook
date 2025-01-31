from django.urls import path
from webook.api.views.service_account_views import (
    service_account_list,
    service_account_detail,
)

app_name = "api"
urlpatterns = [
    path(
        "service_accounts/<int:service_account_id>/",
        service_account_detail,
        name="service_account_detail",
    ),
    path("service_accounts/", service_account_list, name="service_account_list"),
]
