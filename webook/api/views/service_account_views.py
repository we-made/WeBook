from django.views.generic import DetailView, ListView, TemplateView
from webook.api.models import ServiceAccount, APIScope


class ServiceAccountListView(ListView):
    model = ServiceAccount
    template_name = "service_account_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scopes"] = APIScope.objects.all()
        return context


service_account_list = ServiceAccountListView.as_view()


class ServiceAccountDetailView(DetailView):
    pk_url_kwarg = "service_account_id"
    model = ServiceAccount
    template_name = "service_account_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scopes"] = APIScope.objects.all()
        return context


service_account_detail = ServiceAccountDetailView.as_view()
