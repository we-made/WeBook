from django import forms
from webook.arrangement.models import Arrangement


class UploadFilesToEventSerieForm(forms.Form):
    event_serie_pk = forms.SlugField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
