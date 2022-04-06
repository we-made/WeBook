from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceType, Event

class OrderRoomForSerieForm (forms.Form):
    serie_guid = forms.UUIDField()
    room_ids = forms.CharField()

    def is_guid_known():
        pass

    def save():
        pass