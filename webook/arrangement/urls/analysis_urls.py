from django.urls import path

from webook.arrangement.views import (
    analyze_arrangement_view,
    analyze_non_existant_event_view,
    analyze_non_existent_serie_manifest_view,
)

analysis_urls = [
    path(
        route="analysis/analyzeNonExistentSerie",
        view=analyze_non_existent_serie_manifest_view,
        name="analyze_non_existent_serie",
    ),
    path(
        route="analysis/analyzeNonExistentEvent",
        view=analyze_non_existant_event_view,
        name="analyze_non_existent_event",
    ),
    path(
        route="analysis/analyzeArrangement",
        view=analyze_arrangement_view,
        name="analyze_arrangement"
    ),
]
