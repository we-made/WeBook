from django.urls import path
from webook.celery_haystack import views

app_name = "celery_haystack"
urlpatterns = [
    path(
        "list",
        views.TaskResultListView.as_view(),
        name="taskresult_list",
    ),
    path(
        "detail/<int:pk>",
        views.TaskResultDetailView.as_view(),
        name="taskresult_detail",
    ),
]
