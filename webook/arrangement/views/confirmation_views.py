from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
from webook.arrangement.models import ConfirmationReceipt


class ViewConfirmationRequestView(DetailView):
    model = ConfirmationReceipt
    template_name = "arrangement/confirmation/view_confirmation_request.html"