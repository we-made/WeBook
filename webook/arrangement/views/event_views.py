from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    RedirectView,
    TemplateView,
    UpdateView,
    View,
)

from webook.arrangement.forms.event_forms import CreateEventForm, UpdateEventForm
from webook.arrangement.forms.exclusivity_analysis.serie_manifest_form import CreateSerieForm, SerieManifestForm
from webook.arrangement.models import Arrangement, Event, EventSerie, EventSerieFile, Person, PlanManifest, Room
from webook.arrangement.views.generic_views.archive_view import JsonArchiveView
from webook.arrangement.views.generic_views.json_form_view import JsonFormView, JsonModelFormMixin
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin
from webook.screenshow.models import DisplayLayout
from webook.utils.collision_analysis import analyze_collisions
from webook.utils.serie_calculator import calculate_serie


class CreateEventSerieJsonFormView(LoginRequiredMixin, JsonFormView):
    """ Create a new event serie / schedule """
    form_class = CreateSerieForm

    def form_valid(self, form) -> JsonResponse:
        form.save(form)
        return super().form_valid(form)

create_event_serie_json_view = CreateEventSerieJsonFormView.as_view()


class CreateEventJsonFormView(LoginRequiredMixin, CreateView, JsonModelFormMixin):
    """ View for event creation """
    form_class = CreateEventForm
    model = Event

create_event_json_view = CreateEventJsonFormView.as_view()


class UpdateEventJsonFormView(LoginRequiredMixin, UpdateView, JsonModelFormMixin):
    """ Update event """
    model = Event
    form_class = UpdateEventForm

update_event_json_view = UpdateEventJsonFormView.as_view()


class DeleteEventJsonView(LoginRequiredMixin, JsonArchiveView):
    """ Delete event """
    model = Event

delete_event_json_view = DeleteEventJsonView.as_view()

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


class CalculateEventSerieView(LoginRequiredMixin, DetailView, JSONResponseMixin):
    model = PlanManifest
    pk_url_kwarg = "pk"

    def get_object(self):
        serie_pk = self.kwargs.get(self.pk_url_kwarg)
        event_serie = EventSerie.objects.filter(pk=serie_pk).first()
        
        if (event_serie is None):
            raise Http404("No event_serie found matching the query")
        
        return calculate_serie(event_serie.serie_plan_manifest)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_json_response(context, safe=False)

    def get_data(self, context):
        events = context["object"]

        converted_events = []
        for event in events:
            converted_events.append({
                "title": event.title,
                "start": event.start,
                "end": event.end,
            })

        return converted_events

calculate_event_serie_view = CalculateEventSerieView.as_view()


class CalculateEventSeriePreviewView(LoginRequiredMixin, DetailView):
    """ Preview calendar primarily used for testing and debugging the results of a calculation """
    model = PlanManifest
    pk_url_kwarg = "pk"
    template_name = "arrangement/eventserie/preview_calendar.html"

calculate_event_serie_preview_view = CalculateEventSeriePreviewView.as_view()


class EventSerieManifestView(LoginRequiredMixin, DetailView, JSONResponseMixin):
    """
        EventSerieManifestView takes a given EventSerie, and serves the manifest used to generate
        that serie out in JSON format.
    """
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
        