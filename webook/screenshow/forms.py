from django import forms

from webook.screenshow.models import DisplayLayout, ScreenGroup, ScreenResource


class ScreenGroupForm(forms.ModelForm):

    class Meta:
        model = ScreenGroup
        fields = '__all__'

    screens = forms.ModelMultipleChoiceField(
        queryset=ScreenResource.objects.all(),
        widget=forms.CheckboxSelectMultiple, required=False
    )


class DisplayLayoutForm(forms.ModelForm):

    class Meta:
        model = DisplayLayout
        fields = '__all__'

    screens = forms.ModelMultipleChoiceField(
        queryset=ScreenResource.objects.all(),
        widget=forms.CheckboxSelectMultiple, required=False
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=ScreenGroup.objects.all(),
        widget=forms.CheckboxSelectMultiple, required=False
    )
