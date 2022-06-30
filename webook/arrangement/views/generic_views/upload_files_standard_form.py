from django.http import JsonResponse

from webook.arrangement.forms.upload_files_form import UploadFilesForm
from webook.arrangement.views.generic_views.json_form_view import JsonFormView


class UploadFilesStandardFormView(JsonFormView):
    """ A re-usable standard json formview that standardizes uploading and saving of file relationships, using UploadFilesForm.
    Can handle multiple files.

    To use this view you would want a relationship model that inherits from the abstract model BaseFileRelAbstractModel.
    From that point on all you need is to define file_relationship_model (the object of the inherited class) on your view.
    Subsequently uploads and saving will be handled, and no specific logic for this must be written.

    Practically you must define;
    1. model (the model object of the instance you are associating a file with, for example an Event)
    2. file_relationship_model (the model object which you have inherited from BaseFileRelAbstractModel)
    """
    def __init__(self, **kwargs) -> None:
        self._sanity_check_self()
        return super().__init__(**kwargs)

    def _sanity_check_self(self):
        """Sanity check self to see if we have the requisite attributes that we need"""
        if not hasattr(self, "file_relationship_model"):
            raise TypeError("attribute file_relationship_model does not exist")
        if not hasattr(self, "model"):
            raise TypeError("attribute model does not exist")

    form_class = UploadFilesForm

    def form_valid(self, form) -> JsonResponse:
        form.save(
            model=self.model,
            file_relationship_model=self.file_relationship_model,
            uploader=self.request.user.person,
            files=self.request.FILES.getlist('file_field')
        )

        """
        Handling multiple files in Django Forms is unfortunately not supported. This appears to be a bug, as if one
        accesses self.cleaned_data["file_field"] in the save method one gets the last file. To avoid this issue we get the
        files through the request object - this is not entirely ideal, as it makes for a somewhat unclean separation, but
        it works.
        
        To understand why, read: 
        https://stackoverflow.com/questions/46318587/django-uploading-multiple-files-list-of-files-needed-in-cleaned-datafile
        """

        return super().form_valid(form)
