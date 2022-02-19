from unicodedata import name
from django.urls import path
from webook.arrangement import views
from webook.arrangement.views import (
    plan_arrangement_view,
    plan_create_event,
    plan_get_events,
    plan_update_event,
    plan_delete_event,
    planner_view,
    plan_delete_events,
    plan_order_service_view,
    plan_create_events,
)


planner_urls = [
    path(
        route="planner/planner",
        view=planner_view,
        name="planner",
    ),
    path(
        route="planner/plan",
        view=plan_arrangement_view,
        name="plan_arrangement"
    ),
    path(
        route="planner/create_event",
        view=plan_create_event,
        name="plan_create_event"
    ),
    path(
        route="planner/get_events",
        view=plan_get_events,
        name="plan_get_events",
    ),
    path(
        route="planner/update_event/<int:pk>",
        view=plan_update_event,
        name="plan_update_event",
    ),
    path(
        route="planner/delete_event/<int:pk>",
        view=plan_delete_event,
        name="plan_delete_event"
    ),
    path(
        route="planner/delete_events/",
        view=plan_delete_events,
        name="plan_delete_events",
    ),
    path(
        route="planner/order_service/",
        view=plan_order_service_view,
        name="plan_order_service",
    ),
    path(
        route="planner/create_events/",
        view=plan_create_events,
        name="plan_create_events",
    ),
]