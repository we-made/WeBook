from django import forms
from webook.arrangement.models import Arrangement


class UploadFilesToArrangementForm(forms.Form):
    arrangement_slug = forms.SlugField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
