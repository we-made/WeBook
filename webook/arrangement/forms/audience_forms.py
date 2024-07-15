from django import forms

from webook.arrangement.models import Audience

_ALWAYS_FIELDS = (  "name",
                    "name_en",
                    "icon_class",
                    "parent", )


class BaseAudienceForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Audience.objects.filter(parent__isnull=True),
                                    widget=forms.Select(attrs={"class": "form-control"}),
                                    required=False)
    name_en = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Audience
        fields = _ALWAYS_FIELDS


class UpdateAudienceForm(BaseAudienceForm):
    pass


class CreateAudienceForm(BaseAudienceForm):
    pass
