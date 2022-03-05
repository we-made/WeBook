from django import forms
from webook.arrangement.models import LooseServiceRequisition, ServiceRequisition, RequisitionRecord, ServiceType, Event, ServiceProvidable, Person, ConfirmationReceipt
from webook.arrangement.facilities.confirmation_request import confirmation_request_facility

class OrderServiceForm (forms.Form):
    loose_requisition_id = forms.IntegerField()
    provider_id = forms.IntegerField()
    order_information = forms.CharField()

    def save(self):
        loose_requisition = LooseServiceRequisition.objects.get(id=self.cleaned_data["loose_requisition_id"])
        provider = ServiceProvidable.objects.get(id=self.cleaned_data["provider_id"])

        (send_mail_is_success, receipt) = confirmation_request_facility.make_request(
            provider.service_contact, 
            requested_by=Person.objects.first(), 
            request_type=ConfirmationReceipt.TYPE_REQUISITION_SERVICE,
            requisition_record=loose_requisition.generated_requisition_record)

        service_requisition = ServiceRequisition()
        service_requisition.parent_record = loose_requisition.generated_requisition_record
        service_requisition.confirmation_receipt = receipt
        service_requisition.order_information = self.cleaned_data["order_information"]
        service_requisition.provider = provider
        service_requisition.originating_loose_requisition = loose_requisition
        service_requisition.save()

        loose_requisition.save()
        

