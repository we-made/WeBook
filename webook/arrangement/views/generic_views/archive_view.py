from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import DeleteView


class ArchiveView(DeleteView):
    """
        View for archiving an entity, superceding the DeleteView functionality.
    """
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """ 
            Archive the object by calling archive() method on the fetched object and then 
            redirect to success URL
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.archive(request.user.person)
        return HttpResponseRedirect(success_url)


class JsonArchiveView(DeleteView):
    """
        Same as ArchiveView, but returning a JsonResponse instead of HttpResponseRedirect
    """
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """ 
            Archive the object by calling archive() method on the fetched object and then 
            redirect to success URL
        """
        self.object = self.get_object()
        self.object.archive(request.user.person)
        return JsonResponse({'id': self.object.pk})