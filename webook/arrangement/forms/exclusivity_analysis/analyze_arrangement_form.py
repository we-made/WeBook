from django import forms

from webook.arrangement.models import Arrangement, Event


class AnalyzeArrangementForm(forms.Form):
    arrangement_id = forms.IntegerField()

    def get_arrangement(self):
        arrangement_pk = self.cleaned_data["arrangement_id"]
        
        if not arrangement_pk or not arrangement_pk.isdecimal():
            raise ValueError("Invalid arrangement id")

        arrangement = Arrangement.objects.get(id=arrangement_pk)

        if arrangement is None:
            raise Exception("Arrangement with the given ID does not exist")

        return arrangement
