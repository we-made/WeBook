from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.db.models import fields
from django.utils.translation import gettext_lazy as _
from django import forms as dj_forms

from allauth.account.forms import SignupForm

User = get_user_model()


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        fields = ()
        field_classes = {}
        model = User

class UserCreationForm(SignupForm):

    name = dj_forms.CharField(max_length=512, label="Navn")
    
    def save (self, request):
        user = super(UserCreationForm, self).save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user
