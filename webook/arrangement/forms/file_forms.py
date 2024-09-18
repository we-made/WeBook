from typing import List, Type

from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from webook.arrangement.models import BaseFileRelAbstractModel, Person


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class UploadFilesForm(forms.Form):
    pk = forms.IntegerField(required=False)
    slug = forms.SlugField(required=False)
    file_field = MultipleFileField()

    def _get_instance(self, model):
        """Sanity check that the model has the requisite fields"""
        if hasattr(model, "slug") and self.cleaned_data["slug"]:
            return model.objects.get(slug=self.cleaned_data["slug"])
        if hasattr(model, "pk") and self.cleaned_data["pk"]:
            return model.objects.get(pk=self.cleaned_data["pk"])

        raise TypeError("Could not get instance. Have you supplied a slug or a pk?")

    def save(
        self,
        model,
        file_relationship_model: Type[BaseFileRelAbstractModel],
        uploader: Person,
        files: List[InMemoryUploadedFile],
    ):
        for file in files:
            f_rel = file_relationship_model()
            f_rel.associated_with = self._get_instance(model)
            f_rel.uploader = uploader
            f_rel.file = file
            f_rel.save()


class UploadFilesToArrangementForm(forms.Form):
    arrangement_slug = forms.SlugField()
    file_field = MultipleFileField()


class UploadFilesToEventSerieForm(forms.Form):
    event_serie_pk = forms.SlugField()
    file_field = MultipleFileField()
