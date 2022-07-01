from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import DeleteView


class JsonDeleteView(DeleteView):
    """
        Same as DeleteView, but returning a JsonResponse instead of HttpResponseRedirect
    """
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """ 
            Delete the object by calling delete() method on the fetched object and then 
            redirect to success URL
        """
        self.object = self.get_object()
        pk = self.object.pk
        self.object.delete()

        return JsonResponse({'id': pk})
