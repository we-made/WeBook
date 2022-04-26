from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django.contrib import messages


####
# Heartfelt thanks to: https://stackoverflow.com/a/23505267
####


class MultiRedirectMixin(object):
    """
    A mixin that supports submit-specific success redirection.
     Either specify one success_url, or provide dict with names of 
     submit actions given in template as keys
     Example: 
       In template:
         <input type="submit" name="create_new" value="Create"/>
         <input type="submit" name="delete" value="Delete"/>
       View:
         MyMultiSubmitView(MultiRedirectMixin, forms.FormView):
             success_urls = {"create_new": reverse_lazy('create'),
                               "delete": reverse_lazy('delete')}
    """
    success_urls_and_messages = {}

    def form_valid(self, form):
        """ Form is valid: Pick the url and redirect.
        """
    
        for name in self.success_urls_and_messages:
            if name in form.data:
                url_dict = self.success_urls_and_messages[name]
                self.success_url = url_dict["url"]
                if "msg" in url_dict:
                    self.message = url_dict["msg"]
                break

        if hasattr(self, "message") and self.message is not None:
            messages.success(self.request, self.message)

        form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            raise ImproperlyConfigured(
                _("No URL to redirect to. Provide a success_url."))
        return url