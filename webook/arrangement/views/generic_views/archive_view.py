from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import DeleteView


class ArchiveView(DeleteView):
    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """ 
            Archive the object by calling archive() method on the fetched object and then 
            redirect to success URL
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.archive(request.user.person)
        return HttpResponseRedirect(success_url)