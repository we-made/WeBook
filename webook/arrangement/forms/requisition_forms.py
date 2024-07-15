from django import forms

from webook.arrangement.facilities.confirmation_request import confirmation_request_facility
from webook.arrangement.facilities.requisitioning import requisitioning_facility
from webook.arrangement.models import Arrangement, ConfirmationReceipt, LooseServiceRequisition, Person


class RequisitionPersonForm (forms.Form):
    """
        Form for handling requisitioning a person for events he is registered to on 
        arrangement, as identified by arrangement_id
    """
    person_id = forms.IntegerField()
    arrangement_id = forms.IntegerField()

    def save(self):
        person = Person.objects.get(id=self.cleaned_data["person_id"])
        arrangement = Arrangement.objects.get(id=self.cleaned_data["arrangement_id"])
        
        requisitioning_facility.requisition_person(
            requisitioned_person=person,
            requisitioneer=Person.objects.last(),
            arrangement=arrangement
        )


class RequisitionServiceForm (forms.Form):
    pass


class ResetRequisitionForm(forms.Form):
    loose_service_requisition_id = forms.IntegerField()

    def reset(self):
        loose_service_requisition =  LooseServiceRequisition.objects.get(id=self.cleaned_data["loose_service_requisition_id"])
        requisition_record = loose_service_requisition.generated_requisition_record
        actual_requisition = loose_service_requisition.actual_requisition

        actual_requisition.originating_loose_requisition = None
        loose_service_requisition.generated_requisition_record = None
        loose_service_requisition.save()
        

        # requisition_record.delete()
        # actual_requisition.delete()

        loose_service_requisition.save()


class CancelServiceRequisitionForm(forms.Form):
    loose_service_requisition_id = forms.IntegerField()

    def cancel_service_requisition(self):
        loose_service_requisition =  LooseServiceRequisition.objects.get(id=self.cleaned_data["loose_service_requisition_id"])
        
        confirmation_request_facility.cancel_request(
            code=loose_service_requisition.generated_requisition_record.confirmation_receipt.code
        )


class DenyConfirmationRequestForm (forms.Form):
    token = forms.CharField()
    reasoning = forms.CharField()

    def perform_denial(self, confirmation_receipt:ConfirmationReceipt):
        confirmation_request_facility.deny_request(
            code=confirmation_receipt.code, 
            denial_reason=self.cleaned_data["reasoning"])
