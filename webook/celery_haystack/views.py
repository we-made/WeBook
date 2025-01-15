from django.views.generic import DetailView, ListView, TemplateView
from django_celery_results.models import TaskResult, TASK_STATE_CHOICES


class TaskResultListView(ListView):
    template_name = "taskresult_list.html"
    model = TaskResult

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_states"] = TASK_STATE_CHOICES
        context["task_names"] = TaskResult.objects.values_list(
            "task_name", flat=True
        ).distinct()

        return context


class TaskResultDetailView(DetailView):
    template_name = "taskresult_detail.html"
    model = TaskResult
