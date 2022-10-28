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
from webook.arrangement.forms.exclusivity_analysis.serie_manifest_form import (
    CreateSerieForm,
    SerieManifestForm,
)
from webook.arrangement.forms.file_forms import UploadFilesForm
from webook.arrangement.models import (
    Arrangement,
    Event,
    EventFile,
    EventSerie,
    EventSerieFile,
    Person,
    PlanManifest,
    Room,
    RoomPreset,
)
from webook.arrangement.views.generic_views.archive_view import JsonArchiveView
from webook.arrangement.views.generic_views.delete_view import JsonDeleteView
from webook.arrangement.views.generic_views.json_form_view import (
    JsonFormView,
    JsonModelFormMixin,
)
from webook.arrangement.views.generic_views.upload_files_standard_form import (
    UploadFilesStandardFormView,
)
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin
from webook.authorization_mixins import PlannerAuthorizationMixin
from webook.screenshow.models import DisplayLayout
from webook.utils.collision_analysis import analyze_collisions
from webook.utils.serie_calculator import calculate_serie


class CreateEventSerieJsonFormView(
    LoginRequiredMixin, PlannerAuthorizationMixin, JsonFormView
):
    """Create a new event serie / schedule"""

    form_class = CreateSerieForm

    def form_valid(self, form) -> JsonResponse:
        form.save(form, user=self.request.user)
        return super().form_valid(form)


create_event_serie_json_view = CreateEventSerieJsonFormView.as_view()


class CreateEventJsonFormView(
    LoginRequiredMixin, PlannerAuthorizationMixin, CreateView, JsonModelFormMixin
):
    """View for event creation"""

    form_class = CreateEventForm
    model = Event


create_event_json_view = CreateEventJsonFormView.as_view()


class UpdateEventJsonFormView(
    LoginRequiredMixin, PlannerAuthorizationMixin, UpdateView, JsonModelFormMixin
):
    """Update event"""

    model = Event
    form_class = UpdateEventForm


update_event_json_view = UpdateEventJsonFormView.as_view()


class DeleteEventJsonView(
    LoginRequiredMixin, PlannerAuthorizationMixin, JsonArchiveView
):
    """Delete event"""

    model = Event


delete_event_json_view = DeleteEventJsonView.as_view()


class UploadFilesToEventJsonFormView(
    LoginRequiredMixin, PlannerAuthorizationMixin, UploadFilesStandardFormView
):
    """FormView that handles file uploads to an event"""

    model = Event
    file_relationship_model = EventFile


upload_files_to_event_json_form_view = UploadFilesToEventJsonFormView.as_view()


class DeleteFileFromEventView(
    LoginRequiredMixin, PlannerAuthorizationMixin, JsonDeleteView
):
    """View that provides functionality for deleting a file from an event"""

    model = EventFile
    pk_url_kwarg = "pk"


delete_file_from_event_view = DeleteFileFromEventView.as_view()


class UploadFilesToEventSerieJsonFormView(
    LoginRequiredMixin, PlannerAuthorizationMixin, UploadFilesStandardFormView
):
    model = EventSerie
    file_relationship_model = EventSerieFile


upload_files_to_event_serie_json_form_view = (
    UploadFilesToEventSerieJsonFormView.as_view()
)


class EventSerieDeleteFileView(
    LoginRequiredMixin, PlannerAuthorizationMixin, JsonDeleteView
):
    model = EventSerieFile
    pk_url_kwarg = "pk"


event_serie_delete_file_view = EventSerieDeleteFileView.as_view()


class DeleteEventSerie(LoginRequiredMixin, PlannerAuthorizationMixin, JsonArchiveView):
    model = EventSerie
    pk_url_kwarg = "pk"


delete_event_serie_view = DeleteEventSerie.as_view()


class CalculateEventSerieView(
    LoginRequiredMixin, PlannerAuthorizationMixin, DetailView, JSONResponseMixin
):
    model = PlanManifest
    pk_url_kwarg = "pk"

    def get_object(self):
        serie_pk = self.kwargs.get(self.pk_url_kwarg)
        event_serie = EventSerie.objects.filter(pk=serie_pk).first()

        if event_serie is None:
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
            converted_events.append(
                {
                    "title": event.title,
                    "start": event.start,
                    "end": event.end,
                }
            )

        return converted_events


calculate_event_serie_view = CalculateEventSerieView.as_view()


class CalculateEventSeriePreviewView(
    LoginRequiredMixin, PlannerAuthorizationMixin, DetailView
):
    """Preview calendar primarily used for testing and debugging the results of a calculation"""

    model = PlanManifest
    pk_url_kwarg = "pk"
    template_name = "arrangement/eventserie/preview_calendar.html"


calculate_event_serie_preview_view = CalculateEventSeriePreviewView.as_view()


class EventSerieManifestView(
    LoginRequiredMixin, PlannerAuthorizationMixin, DetailView, JSONResponseMixin
):
    """
    EventSerieManifestView takes a given EventSerie, and serves the manifest used to generate
    that serie out in JSON format.
    """

    model = PlanManifest
    pk_url_kwarg = "pk"

    def get_object(self):
        serie_pk = self.kwargs.get(self.pk_url_kwarg)
        event_serie = EventSerie.objects.filter(pk=serie_pk).first()

        if event_serie is None:
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

        for display_layout in manifest.display_layouts.all():
            display_layouts.append(
                {"id": display_layout.id, "name": display_layout.name}
            )

        room_presets = RoomPreset.objects.all()
        selected_rooms = {
            "allPresets": {
                room_preset.slug: room_preset.name for room_preset in room_presets
            },
            "allSelectedEntityIds": [],
            "viewables": [],
            "selectedPresets": [],
            "eventPk": "",
        }

        rooms = {room.id: room.name for room in manifest.rooms.all()}
        viewables = {**rooms}
        room_ids = set([room for room in rooms.keys()])

        for a_room_preset in room_presets:
            room_preset_member_rooms = set(
                [room.id for room in a_room_preset.rooms.all()]
            )
            if room_preset_member_rooms.issubset(room_ids):
                selected_rooms["selectedPresets"].append(a_room_preset.slug)
                viewables[a_room_preset.slug] = a_room_preset.name
                for room_id in room_preset_member_rooms:
                    del viewables[room_id]

        selected_rooms["viewables"] = [
            {"id": key, "text": value} for (key, value) in viewables.items()
        ]
        selected_rooms["allSelectedEntityIds"] = [
            {"id": key, "text": value} for (key, value) in rooms.items()
        ]

        people = [
            {"id": person.id, "text": person.full_name}
            for person in manifest.people.all()
        ]
        selected_people = {
            "allPresets": [],
            "allSelectedEntityIds": people,
            "viewables": people,
            "selectedPresets": [],
            "eventPk": "",
        }

        responsible_list = (
            [{"id": manifest.responsible.id, "text": manifest.responsible.full_name}]
            if manifest.responsible
            else []
        )
        responsible = {
            "allPresets": [],
            "allSelectedEntityIds": responsible_list,
            "viewables": responsible_list,
            "selectedPresets": [],
            "eventPk": "",
        }

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
            "before_buffer_title": manifest.before_buffer_title,
            "before_buffer_date_offset": manifest.before_buffer_date_offset,
            "before_buffer_start": manifest.before_buffer_start,
            "before_buffer_end": manifest.before_buffer_end,
            "after_buffer_title": manifest.after_buffer_title,
            "after_buffer_date_offset": manifest.after_buffer_date_offset,
            "after_buffer_start": manifest.after_buffer_start,
            "after_buffer_end": manifest.after_buffer_end,
            "stop_within": manifest.stop_within,
            "stop_after_x_occurences": manifest.stop_after_x_occurences,
            "project_x_months_into_future": manifest.project_x_months_into_future,
            "rooms": selected_rooms,
            "people": selected_people,
            "display_layouts": display_layouts,
            "display_text": manifest.display_text,
            "display_text_en": manifest.display_text_en,
            "meeting_place": manifest.meeting_place,
            "meeting_place_en": manifest.meeting_place_en,
            "status": manifest.status.pk if manifest.status else None,
            "audience": manifest.audience.pk if manifest.audience else None,
            "arrangement_type": manifest.arrangement_type.pk
            if manifest.arrangement_type
            else None,
            "responsible": responsible,
        }


event_serie_manifest_view = EventSerieManifestView.as_view()
