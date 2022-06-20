from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView, UpdateView, View

from webook.arrangement.forms.exclusivity_analysis.serie_manifest_form import CreateSerieForm, SerieManifestForm
from webook.arrangement.models import Arrangement, Event, EventSerie
from webook.arrangement.views.generic_views.json_form_view import JsonFormView, JsonModelFormMixin
from webook.utils.collision_analysis import analyze_collisions
from webook.utils.serie_calculator import calculate_serie


class CreateEventSerieJsonFormView(LoginRequiredMixin, JsonFormView):
    """ Create a new event serie / schedule """
    form_class = CreateSerieForm

    def form_valid(self, form) -> JsonResponse:
        manifest = form.as_plan_manifest()
        calculated_serie = calculate_serie(manifest)

        for ev in calculated_serie:
            ev.rooms = [int(room.id) for room in manifest.rooms.all()]

        _ = analyze_collisions(calculated_serie)

        serie = EventSerie()
        serie.arrangement = Arrangement.objects.get(slug=form.cleaned_data["arrangement_slug"])
        serie.manifest = manifest
        serie.save()

        for ev in calculated_serie:
            if ev.is_collision:
                continue
            
            event = Event()
            event.title = manifest.title
            event.title_en = manifest.title_en
            event.ticket_code = manifest.ticket_code
            event.rooms = manifest.rooms
            event.people = manifest.people
            event.display_layouts = manifest.display_layouts
            event.expected_visitors = manifest.expected_visitors
            event.serie = serie
            event.save()
        
        return super().form_valid(form)

create_event_serie_json_view = CreateEventSerieJsonFormView.as_view()


class CreateEventJsonFormView(LoginRequiredMixin, CreateView, JsonModelFormMixin):
    """ View for event creation """
    model = Event

create_event_json_view = CreateEventJsonFormView.as_view()
