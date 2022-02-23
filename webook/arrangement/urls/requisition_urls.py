from unicodedata import name
from django.urls import path
from webook.arrangement import views
from webook.arrangement.views import (
    requisition_dashboard_view,
    requisitions_on_event_component_view,
    requisitions_on_arrangement_component_view,
    remove_event_from_requisition_view,
    delete_requisition_view,
    requisition_service_form_view
)


requisition_urls = [
    path(
        route="requisition/dashboard",
        view=requisition_dashboard_view,
        name="requisitions_dashboard",
    ),
    path(
        route="requisition/requisitions_on_event",
        view=requisitions_on_event_component_view,
        name="requisitions_on_event",
    ),
    path(
        route="requisition/requisitions_on_arrangement",
        view=requisitions_on_arrangement_component_view,
        name="requisitions_on_arrangement",
    ),
    path(
        route="requisition/remove_event_from_requisition",
        view=remove_event_from_requisition_view,
        name="remove_event_from_requisition",
    ),
    path(
        route="requisition/delete_requisition",
        view=delete_requisition_view,
        name="delete_requisition",
    ),
    path(
        route="requisition/<int:lreq_id>/order",
        view=requisition_service_form_view,
        name="order_service_form",
    )
]
