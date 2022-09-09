from django.http import JsonResponse
from django.views.generic import ListView


class JsonListView(ListView):
    """ ListView returning QuerySet / object_list as json """
    def render_to_response(self, context, **response_kwargs) -> JsonResponse:
        """ Override render_to_response and return a object_list in JsonResponse """
        return JsonResponse(self.object_list, safe=False)
