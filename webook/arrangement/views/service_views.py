import datetime
import json
from re import search
from typing import Any, Dict, List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models import F, Q
from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
)
from django.views.generic.base import View
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
)
from django.views.generic.edit import DeleteView, FormMixin

from webook.arrangement.forms.person_forms import AssociatePersonWithUserForm
from webook.arrangement.forms.service_forms import (
    AddEmailForm,
    AddPersonForm,
    DeleteEmailForm,
)
from webook.arrangement.models import (
    Organization,
    Person,
    Service,
    ServiceOrder,
    ServiceOrderProcessingRequest,
    States,
)
from webook.arrangement.views.generic_views.archive_view import (
    ArchiveView,
    JsonArchiveView,
    JsonToggleArchiveView,
)
from webook.arrangement.views.generic_views.delete_view import JsonDeleteView
from webook.arrangement.views.generic_views.json_form_view import JsonFormView
from webook.arrangement.views.generic_views.search_view import SearchView
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin
from webook.arrangement.views.mixins.multi_redirect_mixin import MultiRedirectMixin
from webook.arrangement.views.organization_views import OrganizationSectionManifestMixin
from webook.authorization_mixins import PlannerAuthorizationMixin
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.json_serial import json_serial
from webook.utils.meta_utils import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.meta_utils.section_manifest import SUBTITLE_MODE, SectionManifest
from webook.utils.reverse_with_params import reverse_with_params

# def get_section_manifest():
#     return SectionManifest(
#         section_title=_("People"),
#         section_icon="fas fa-users",
#         section_crumb_url=reverse("arrangement:location_list"),
#         crudl_map=SectionCrudlPathMap(
#             detail_url="arrangement:person_detail",
#             create_url="arrangement:person_create",
#             edit_url="arrangement:person_edit",
#             delete_url="arrangement:person_delete",
#             list_url="arrangement:person_list",
#         ),
#     )


# class ServiceSectionManifestMixin:
#     def __init__(self) -> None:
#         super().__init__()
#         self.section = get_section_manifest()


class ServicesDashboardView(
    LoginRequiredMixin, TemplateView, PlannerAuthorizationMixin
):
    template_name = "arrangement/service/list.html"


services_dashboard_view = ServicesDashboardView.as_view()


class ServicesJsonListView(LoginRequiredMixin, ListView, JSONResponseMixin):
    model = Service

    def transform_queryset(self, queryset) -> List[Dict]:
        result: List[Dict] = []
        for service in queryset.all():
            result.append(
                {
                    "isArchived": service.is_archived,
                    "editUrl": f"/arrangement/service/{service.id}/update",
                    "id": service.id,
                    "name": service.name,
                    "emails": list(service.emails.values_list("email", flat=True)),
                    "templates": [
                        {
                            "title": t.line_title,
                            "assigned_personell": t.assigned_personell,
                            "comment": t.freetext_comment,
                        }
                        for t in service.associated_lines.filter(
                            state=States.TEMPLATE
                        ).all()
                    ],
                    "resources": [
                        person.full_name for person in service.resources.all()
                    ],
                }
            )
        return result

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return self.render_to_json_response(
            self.transform_queryset(Service.all_objects), safe=False
        )


services_json_list_view = ServicesJsonListView.as_view()


class ServiceAddEmailView(LoginRequiredMixin, JsonFormView):
    form_class = AddEmailForm
    template_name = "arrangement/service/add_email.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["SERVICE_ID"] = kwargs.get("pk")
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


services_add_email_view = ServiceAddEmailView.as_view()


class ServiceAddPersonDialog(LoginRequiredMixin, UpdateView, JsonFormView):
    model = Service
    form_class = AddPersonForm
    slug_field = "id"
    slug_url_kwarg = "id"
    template_name = "arrangement/service/add_person.html"

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["SERVICE_ID"] = kwargs.get("pk")
        return context


services_add_person_view = ServiceAddPersonDialog.as_view()


class CreateServiceView(LoginRequiredMixin, CreateView, JsonFormView):
    model = Service
    template_name = "arrangement/service/form.html"
    fields = ["name"]

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


create_service_view = CreateServiceView.as_view()


class UpdateServiceView(LoginRequiredMixin, UpdateView, JsonFormView):
    model = Service
    fields = ["name"]
    slug_field = "id"
    slug_url_kwarg = "id"
    template_name = "arrangement/service/form.html"

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


update_service_view = UpdateServiceView.as_view()


class ToggleServiceActiveStateJSONView(LoginRequiredMixin, JsonToggleArchiveView):
    model = Service
    pk_url_kwarg = "id"


toggle_service_active_json_view = ToggleServiceActiveStateJSONView.as_view()


class DeleteServiceEmailFromServiceView(LoginRequiredMixin, JsonFormView):
    form_class = DeleteEmailForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


delete_service_email_from_service_view = DeleteServiceEmailFromServiceView.as_view()


class CreateServiceTemplateView(LoginRequiredMixin, CreateView):
    model = ServiceOrder
    template_name = "arrangement/service/new_template.html"
    fields = ["line_title", "sassigned_personell", "freetext_cmment"]


create_service_template_view = CreateServiceTemplateView.as_view()


class ProcessServiceRequestView(DetailView):
    model = ServiceOrderProcessingRequest
    template_name = "arrangement/service/process_request.html"
    slug_field = "code"
    slug_url_kwarg = "token"


process_service_request_view = ProcessServiceRequestView.as_view()
