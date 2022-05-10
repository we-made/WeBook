from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.db.models import Q
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
from django.views.generic.edit import DeleteView
from requests import delete
from webook.arrangement.forms.delete_arrangement_file_form import DeleteArrangementFileForm
from webook.arrangement.forms.planner.planner_create_arrangement_form import PlannerCreateArrangementModelForm
from webook.arrangement.forms.promote_planner_to_main_form import PromotePlannerToMainForm
from webook.arrangement.forms.remove_planner_form import RemovePlannerForm
from webook.arrangement.forms.add_planner_form import AddPlannerForm
from webook.arrangement.models import Arrangement, ArrangementFile, EventSerie, EventSerieFile, Person
from webook.arrangement.views.generic_views.archive_view import ArchiveView, JsonArchiveView
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin
from webook.arrangement.views.search_view import SearchView
from webook.utils.meta_utils.meta_mixin import MetaMixin
from django.views.generic.edit import FormView
from django.http import HttpRequest, HttpResponse, JsonResponse
from webook.utils.meta_utils.section_manifest import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


class EventSerieDeleteFileView(LoginRequiredMixin, DeleteView):
    model = EventSerieFile
    template_name = "_blank.html"

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        payload = { 'delete': 'ok' }
        return JsonResponse(payload)

event_serie_delete_file_view = EventSerieDeleteFileView.as_view()


class DeleteEventSerie(LoginRequiredMixin, JsonArchiveView):
    model = EventSerie
    pk_url_kwarg = "pk"

delete_event_serie_view = DeleteEventSerie.as_view()