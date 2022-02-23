from django import forms
from webook.arrangement.models import LooseServiceRequisition, OrderedService, ServiceType, Event, ServiceProvidable, Person
from webook.arrangement.facilities.confirmation_request import confirmation_request_facility

class OrderServiceForm (forms.Form):
    loose_requisition_id = forms.IntegerField()
    provider_id = forms.IntegerField()
    order_information = forms.CharField()

    def save(self):
        print("==>")
        print("loose_requisition_id: " + str(self.cleaned_data["loose_requisition_id"]))
        print("provider_id: " + str(self.cleaned_data["provider_id"]))
        print("order_information: " + str(self.cleaned_data["order_information"]))

        loose_requisition = LooseServiceRequisition.objects.get(id=self.cleaned_data["loose_requisition_id"])
        provider = ServiceProvidable.objects.get(id=self.cleaned_data["provider_id"])

        print("SERVICE_CONTACT: " + provider.service_contact)

        (send_mail_is_success, receipt) = confirmation_request_facility.make_request(provider.service_contact, requested_by=Person.objects.first())
        order_service = OrderedService()
        order_service.state = OrderedService.STATE_AWAITING_RESPONSE
        order_service.confirmation_receipt = receipt
        order_service.order_information = self.cleaned_data["order_information"]
        order_service.provider = provider
        order_service.save()

        loose_requisition.ordered_service = order_service
        loose_requisition.save()
        

