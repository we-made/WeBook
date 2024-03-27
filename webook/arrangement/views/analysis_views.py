from datetime import datetime, time, timedelta
from typing import List

import pytz
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone as dj_timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView, UpdateView, View

from webook.arrangement.dto.event import EventDTO
from webook.arrangement.forms.exclusivity_analysis.analyze_arrangement_form import AnalyzeArrangementForm
from webook.arrangement.forms.exclusivity_analysis.analyze_non_existant_event import AnalyzeNonExistantEventForm
from webook.arrangement.forms.exclusivity_analysis.serie_manifest_form import SerieManifestForm
from webook.arrangement.views.generic_views.json_form_view import JsonFormView
from webook.authorization_mixins import PlannerAuthorizationMixin
from webook.utils.collision_analysis import CollisionRecord, analyze_collisions
from webook.utils.serie_calculator import _Event, calculate_serie
from webook.utils.sph_gen import get_serie_positional_hash


class CollisionAnalysisFormView(JsonFormView):
    def form_valid(self, form) -> JsonResponse:
        return super().form_valid(form)

    def form_invalid(self, form) -> JsonResponse:
        return super().form_invalid(form)


class AnalyzeNonExistentSerieManifest(
    LoginRequiredMixin, PlannerAuthorizationMixin, CollisionAnalysisFormView
):
    """Analyze a non-existent serie / plan manifest, and return JSON with collisions"""

    form_class = SerieManifestForm

    def form_valid(self, form) -> JsonResponse:
        manifest = form.as_plan_manifest()
        calculated_serie: List[_Event] = calculate_serie(manifest)

        if manifest.exclusions:
            excluded_dates = list(map(lambda ex: ex.date, manifest.exclusions.all()))
            calculated_serie = [
                ev for ev in calculated_serie if ev.start.date() not in excluded_dates
            ]

        converted_events: List[EventDTO] = []

        rooms_list = [int(room.id) for room in manifest.rooms.all()]
        for ev in calculated_serie:
            event_dto = EventDTO(
                title=ev.title,
                start=ev.start,
                end=ev.end,
                rooms=rooms_list,
                before_buffer_title=manifest.before_buffer_title,
                before_buffer_date_offset=manifest.before_buffer_date_offset,
                before_buffer_start=manifest.before_buffer_start,
                before_buffer_end=manifest.before_buffer_end,
                after_buffer_title=manifest.after_buffer_title,
                after_buffer_date_offset=manifest.after_buffer_date_offset,
                after_buffer_start=manifest.after_buffer_start,
                after_buffer_end=manifest.after_buffer_end,
                is_resolution=True,
            )
            rigging_events: dict = event_dto.generate_rigging_events()
            events = []

            # TODO: Figure out if this is necessary, or a remotely intelligent way of doing it.
            # Date should be enough - no?
            event_dto.serie_positional_hash: str = get_serie_positional_hash(
                manifest.internal_uuid, event_dto.title, event_dto.start, event_dto.end
            )

            rigging_before_event = rigging_events.get("before", None)
            if rigging_before_event is not None:
                rigging_before_event.is_rigging = True
                rigging_before_event.sph_of_root_event = event_dto.serie_positional_hash
                rigging_before_event.serie_positional_hash = (
                    rigging_before_event.generate_serie_positional_hash(
                        manifest.internal_uuid
                    )
                )
                events.append(rigging_before_event)
            rigging_after_event = rigging_events.get("after", None)
            if rigging_after_event is not None:
                rigging_after_event.is_rigging = True
                rigging_after_event.sph_of_root_event = event_dto.serie_positional_hash
                rigging_after_event.serie_positional_hash = (
                    rigging_after_event.generate_serie_positional_hash(
                        manifest.internal_uuid
                    )
                )
                events.append(rigging_after_event)

            events.append(event_dto)

            converted_events += events

        pk_of_preceding_event_serie = manifest._predecessor_serie
        records = analyze_collisions(
            converted_events, ignore_serie_pk=pk_of_preceding_event_serie
        )

        # records = {r.event_b_id: r for r in records}.values()

        return JsonResponse([vars(record) for record in records], safe=False)


analyze_non_existent_serie_manifest_view = AnalyzeNonExistentSerieManifest.as_view()


class AnalyzeArrangement(
    LoginRequiredMixin, PlannerAuthorizationMixin, CollisionAnalysisFormView
):
    """Analyze an arrangements events for collisions on exclusivity"""

    form_class = AnalyzeArrangementForm

    def form_valid(self, form) -> JsonResponse:
        return super().form_valid(form)

    def form_invalid(self, form) -> JsonResponse:
        return super().form_invalid(form)


analyze_arrangement_view = AnalyzeArrangement.as_view()


class AnalyzeNonExistantEvent(
    LoginRequiredMixin, PlannerAuthorizationMixin, CollisionAnalysisFormView
):
    """Analyze a non-existent event, and return JSON with collisions"""

    form_class = AnalyzeNonExistantEventForm

    def form_valid(self, form) -> JsonResponse:
        event_dto = form.as_event_dto()
        rigging_events = event_dto.generate_rigging_events()

        events = list(
            filter(
                lambda x: x,
                [
                    rigging_events.get("before", None),
                    event_dto,
                    rigging_events.get("after", None),
                ],
            )
        )

        records = analyze_collisions(events)
        current_tz = pytz.timezone(str(dj_timezone.get_current_timezone()))

        for record in records:
            record.event_a_start = record.event_a_start.astimezone(current_tz)
            record.event_a_end = record.event_a_end.astimezone(current_tz)
            record.event_b_start = record.event_b_start.astimezone(current_tz)
            record.event_b_end = record.event_b_end.astimezone(current_tz)

        return JsonResponse([vars(record) for record in records], safe=False)

    def form_invalid(self, form) -> JsonResponse:
        return super().form_invalid(form)


analyze_non_existant_event_view = AnalyzeNonExistantEvent.as_view()
