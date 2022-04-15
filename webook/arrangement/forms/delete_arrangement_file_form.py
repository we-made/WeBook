from django import forms
from webook.arrangement.models import Arrangement, ArrangementFile, LooseServiceRequisition
from webook.arrangement.facilities.confirmation_request import confirmation_request_facility


class DeleteArrangementFileForm(forms.Form):
    arrangement_slug = forms.SlugField()
    file_id = forms.IntegerField()

    def delete_file(self):
        arrangement_slug = self.cleaned_data["arrangement_slug"]
        file_id = self.cleaned_data["file_id"]
        
        arrangement = Arrangement.objects.get(slug = arrangement_slug)
        arrangement_file = ArrangementFile.get(pk = file_id)

        arrangement.remove(arrangement_file)

        arrangement.save()
