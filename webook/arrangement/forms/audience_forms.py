from django import forms
from webook.arrangement.models import Audience


_ALWAYS_FIELDS = (  "name",
                    "name_en",
                    "icon_class",
                    "parent", )


class BaseAudienceForm(forms.ModelForm):
    class Meta:
        model = Audience
        fields = _ALWAYS_FIELDS
        widgets = { "parent": forms.Select(attrs={"class": "form-control"}) }


class UpdateAudienceForm(BaseAudienceForm):
    pass


class CreateAudienceForm(BaseAudienceForm):
    pass