from django import forms

from webook.arrangement.models import Person


class UploadFilesForm(forms.Form):
    pk = forms.IntegerField(required=False)
    slug = forms.SlugField(required=False)
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

    def _get_instance(self, model):
        """ Sanity check that the model has the requisite fields """
        if hasattr(model, "slug") and self.cleaned_data["slug"]:
            return model.objects.get(slug=self.cleaned_data["slug"])
        if hasattr(model, "pk") and self.cleaned_data["pk"]:
            return model.objects.get(pk=self.cleaned_data["pk"])
        
        raise TypeError("Could not get instance. Have you supplied a slug or a pk?")
            

    def save(self, model, file_relationship_model, uploader: Person, files):
        for file in files:
            f_rel = file_relationship_model()
            f_rel.associated_with = self._get_instance(model)
            f_rel.uploader = uploader
            f_rel.file = file
            f_rel.save()
        
