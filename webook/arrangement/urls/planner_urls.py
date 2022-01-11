from django.urls import path
from webook.arrangement import views
from webook.arrangement.views import (
    plan_arrangement_view
)


planner_urls = [
    path(
        route="planner/plan",
        view=plan_arrangement_view,
        name="plan_arrangement"
    )
]