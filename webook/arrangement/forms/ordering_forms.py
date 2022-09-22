from django import forms

from webook.arrangement.facilities.confirmation_request import confirmation_request_facility
from webook.arrangement.facilities.requisitioning.requisitioning_facility import setup_service_requisition
from webook.arrangement.models import (
    ConfirmationReceipt,
    Event,
    LooseServiceRequisition,
    Person,
    ServiceProvidable,
    ServiceRequisition,
    ServiceType,
)


class LooselyOrderServiceForm (forms.Form):
    events = forms.CharField()
    comment = forms.CharField()
    service_type = forms.IntegerField()

    def save(self):
        requisition = LooseServiceRequisition()
        requisition.comment = self.cleaned_data["comment"]
        requisition.type_to_order = ServiceType.objects.get(pk=self.cleaned_data["service_type"]) if self.cleaned_data["service_type"] is not None else None
        event_ids = self.cleaned_data["events"].split(",") if self.cleaned_data["events"] is not None else []
        requisition.arrangement = Event.objects.get(id=event_ids[0]).arrangement
        requisition.save()
        requisition.events.set(event_ids)

        requisition.save()


class OrderPersonForSerieForm (forms.Form):
    serie_guid = forms.UUIDField()
    people_ids = forms.CharField()

    def is_guid_known():
        pass

    def save(self):
        serie_sequence_guid = self.cleaned_data["serie_guid"]
        person_ids_arr = (self.cleaned_data["people_ids"]).split(",")

        events_in_serie = Event.objects.filter(sequence_guid=serie_sequence_guid)

        for event in events_in_serie:
            for person_id in person_ids_arr:
                event.people.add(person_id)
            event.save()


class OrderRoomForSerieForm (forms.Form):
    serie_guid = forms.UUIDField()
    room_ids = forms.CharField()

    def is_guid_known():
        pass

    def save(self):
        serie_sequence_guid = self.cleaned_data["serie_guid"]
        room_ids_arr = (self.cleaned_data["room_ids"]).split(",")

        events_in_serie = Event.objects.filter(sequence_guid=serie_sequence_guid)

        for event in events_in_serie:
            for room_id in room_ids_arr:
                event.rooms.add(room_id)
            event.save()


class OrderRoomForEventForm(forms.Form):
    event_pk = forms.IntegerField()
    room_ids = forms.CharField()

    def save(self):
        event = Event.objects.get(id=self.cleaned_data["event_pk"])
        room_pks = (self.cleaned_data["room_ids"]).split(",")

        for pk in room_pks:
            event.rooms.add(pk)

        event.save()


class OrderServiceForm (forms.Form):
    loose_requisition_id = forms.IntegerField()
    provider_id = forms.IntegerField()
    order_information = forms.CharField()

    def save(self):
        loose_requisition = LooseServiceRequisition.objects.get(id=self.cleaned_data["loose_requisition_id"])
        provider = ServiceProvidable.objects.get(id=self.cleaned_data["provider_id"])

        record = setup_service_requisition(loose_requisition)
        service_requisition = ServiceRequisition()
        service_requisition.order_information = self.cleaned_data["order_information"]
        service_requisition.provider = provider
        service_requisition.originating_loose_requisition = loose_requisition
        service_requisition.save()

        record.service_requisition = service_requisition
        record.save()


        (send_mail_is_success, receipt) = confirmation_request_facility.make_request(
            provider.service_contact, 
            requested_by=Person.objects.first(), 
            request_type=ConfirmationReceipt.TYPE_REQUISITION_SERVICE,
            requisition_record=record
        )
        
        service_requisition.confirmation_receipt = receipt
        service_requisition.save()

        loose_requisition.save()
        

class OrderPersonForEventForm(forms.Form):
    event_pk = forms.IntegerField()
    people_ids = forms.CharField()

    def save(self):
        event = Event.objects.get(id=self.cleaned_data["event_pk"])
        people_pks = (self.cleaned_data["people_ids"]).split(",")

        for pk in people_pks:
            event.people.add(pk)

        event.save()


class RemoveRoomFromEventForm (forms.Form):
    event_pk = forms.IntegerField()
    room_pk = forms.IntegerField()

    def remove(self):
        cleaned_event_pk = self.cleaned_data["event_pk"]
        cleaned_room_pk = self.cleaned_data["room_pk"]

        event = Event.objects.get(id=cleaned_event_pk)
        event.rooms.remove(cleaned_room_pk)


class RemovePersonFromEventForm (forms.Form):
    event_pk = forms.IntegerField()
    person_pk = forms.IntegerField()

    def remove(self):
        cleaned_event_pk = self.cleaned_data["event_pk"]
        cleaned_person_pk = self.cleaned_data["person_pk"]

        event = Event.objects.get(id=cleaned_event_pk)
        event.people.remove(cleaned_person_pk)
