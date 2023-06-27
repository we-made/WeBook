import json
from enum import Enum
from typing import List, Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

from webook.utils import json_serial


class SearchView(ListView):
    class SearchType(Enum):
        TermSearch = 1
        PkSearch = 2

    def post(self, request):
        body_data = json.loads(request.body.decode("utf-8"))
        search_type = (
            self.SearchType(body_data["search_type"])
            if "search_type" in body_data
            else self.SearchType.TermSearch
        )

        response = None
        if search_type == self.SearchType.TermSearch:
            search_term = body_data["term"]
            response = serializers.serialize("json", self.search(search_term))
        if search_type == self.SearchType.PkSearch:
            pks = body_data["pks"]
            response = serializers.serialize("json", self.pk_search(pks))

        return JsonResponse(response, safe=False)

    def get(self, request):
        search_term = request.GET.get("term", "")

        results: Union[QuerySet, List[dict]] = self.search(search_term)

        if isinstance(results, QuerySet) and hasattr(results, "_meta"):
            response = serializers.serialize("json", results)
        else:
            if isinstance(results, QuerySet):  # values has no _meta
                results = list(results)
            response = json.dumps(results, default=json_serial)

        return JsonResponse(response, safe=False)

    def pk_search(self, pks):
        return self.model.objects.filter(pk__in=pks)

    def search(self, search_term):
        raise NotImplementedError
