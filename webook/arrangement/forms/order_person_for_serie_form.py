from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceType, Event

class OrderPersonForSerieForm (forms.Form):
    serie_guid = forms.UUIDField()
    people_ids = forms.CharField()

    def is_guid_known():
        pass

    def save():
        pass