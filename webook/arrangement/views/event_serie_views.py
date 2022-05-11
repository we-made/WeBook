from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.db.models import Q
from django.core import serializers
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
from webook.arrangement.models import Arrangement, ArrangementFile, EventSerie, EventSerieFile, Person, PlanManifest
from webook.arrangement.views.generic_views.archive_view import ArchiveView, JsonArchiveView
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin
from webook.arrangement.views.generic_views.search_view import SearchView
from webook.utils.meta_utils.meta_mixin import MetaMixin
from django.views.generic.edit import FormView
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
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


class EventSerieManifestView(LoginRequiredMixin, DetailView, JSONResponseMixin):
    model = PlanManifest
    pk_url_kwarg = "pk"

    def get_object(self):
        serie_pk = self.kwargs.get(self.pk_url_kwarg)
        event_serie = EventSerie.objects.filter(pk=serie_pk).first()

        if (event_serie is None):
            raise Http404("No event_serie found matching the query")

        return event_serie.serie_plan_manifest

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_json_response(context)

    def get_data(self, context):
        manifest = context["object"]

        rooms = [] 
        people = []
        display_layouts = []

        for room in manifest.rooms.all():
            rooms.append({
                "id": room.id,
                "name": room.name
            })
        for person in manifest.people.all():
            people.append({
                "id": person.id,
                "name": person.full_name
            })
        for display_layout in manifest.display_layouts.all():
            display_layouts.append({
                "id": display_layout.id,
                "name": display_layout.name
            })

        return {
            "expected_visitors": manifest.expected_visitors,
            "ticket_code": manifest.ticket_code,
            "title": manifest.title,
            "title_en": manifest.title_en,
            "pattern": manifest.pattern,
            "pattern_strategy": manifest.pattern_strategy,
            "recurrence_strategy": manifest.recurrence_strategy,
            "start_date": manifest.start_date,
            "start_time": manifest.start_time,
            "end_time": manifest.end_time,
            "interval": manifest.interval,
            "strategy_specific": {
                "interval": manifest.interval,
                "arbitrator": manifest.arbitrator,
                "days": [
                    manifest.monday,
                    manifest.tuesday,
                    manifest.wednesday,
                    manifest.thursday,
                    manifest.friday,
                    manifest.saturday,
                    manifest.sunday,
                ],
                "day_of_week": manifest.day_of_week,
                "day_of_month": manifest.day_of_month,
                "month": manifest.month,
            },
            "stop_within": manifest.stop_within,
            "stop_after_x_occurences": manifest.stop_after_x_occurences,
            "project_x_months_into_future": manifest.project_x_months_into_future,
            "rooms": rooms,
            "people": people,
            "display_layouts": display_layouts
        }

event_serie_manifest_view = EventSerieManifestView.as_view()
        
