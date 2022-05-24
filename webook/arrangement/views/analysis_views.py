from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView, UpdateView, View

from webook.arrangement.forms.exclusivity_analysis.analyze_non_existent_serie_manifest_form import (
    AnalyzeNonExistentSerieManifestForm,
)
from webook.arrangement.views.generic_views.json_form_view import JsonFormView


class CollisionAnalysisFormView(JsonFormView):
    def form_valid(self, form) -> JsonResponse:
        return super().form_valid(form)

    def form_invalid(self, form) -> JsonResponse:
        return super().form_invalid(form)



class AnalyzeNonExistentSerieManifest(LoginRequiredMixin, CollisionAnalysisFormView):
    """ Analyze a non-existent serie / plan manifest, and return JSON with collisions """
    form_class = AnalyzeNonExistentSerieManifestForm

    def form_valid(self, form) -> JsonResponse:
        print("valid")
        
        return super().form_valid(form)

    def form_invalid(self, form) -> JsonResponse:
        print(form.errors)
        return super().form_invalid(form)

analyze_non_existent_serie_manifest_view = AnalyzeNonExistentSerieManifest.as_view()


class AnalyzeArrangement(LoginRequiredMixin, CollisionAnalysisFormView):
    """ Analyze an arrangements events for collisions on exclusivity """
    pass

analyze_arrangement_view = AnalyzeArrangement.as_view()


class AnalyzeNonExistantEvent(LoginRequiredMixin, CollisionAnalysisFormView):
    """ Analyze a non-existent event, and return JSON with collisions """
    pass

analyze_non_existant_event_view = AnalyzeNonExistantEvent.as_view()
