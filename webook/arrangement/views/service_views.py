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
from django.views.generic.edit import DeleteView, FormMixin

from webook.arrangement.forms.person_forms import AssociatePersonWithUserForm
from webook.arrangement.models import Organization, Person, Service
from webook.arrangement.views.generic_views.archive_view import ArchiveView
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


services_json_list_view = ServicesJsonListView.as_view()


class ServiceAddEmailView(LoginRequiredMixin, FormView, JSONResponseMixin):
    pass


services_add_email_view = ServiceAddEmailView.as_view()


class CreateServiceView(LoginRequiredMixin, CreateView, JSONResponseMixin):
    model = Service


create_service_view = CreateServiceView.as_view()


class UpdateServiceView(LoginRequiredMixin, UpdateView, JSONResponseMixin):
    model = Service


update_service_view = UpdateServiceView.as_view()
