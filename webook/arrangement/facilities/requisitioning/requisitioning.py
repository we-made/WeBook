from webook.arrangement.models import Arrangement, Event, Person, RequisitionRecord
from webook.arrangement.facilities.confirmation_request import confirmation_request_facility


def move_arrangement_to_requisitioning (arrangement: Arrangement, requisitoneer: Person):
    arrangement.stages = Arrangement.REQUISITIONING
    arrangement.save()

    unique_people_to_requisition = arrangement.event_set.all().values('people').distinct()
    orders_to_stage = arrangement.loose_service_requisitions.all()

    requisition_records = []

    for person in unique_people_to_requisition:
        requisition_records.append(requisition_person(person, requisitoneer, arrangement))
    for service in orders_to_stage:
        requisition_records.append(setup_service_requisition(service))

    enact_requisitoning_locks(arrangement.event_set, requisition_records)


def requisition_person(requisitioned_person, requisitioneer, arrangement):
    events_i_am_assigned_to = arrangement.event_set.filter(people__in=[requisitioned_person])
    (was_mail_sent_successfully, confirmation_receipt) = confirmation_request_facility.make_request(requisitioned_person.personal_email, requested_by=requisitioneer)

    # create a requisition record so that we can track the changes optimally
    record = RequisitionRecord()
    record.affected_events = events_i_am_assigned_to
    record.associated_confirmation_receipt = confirmation_receipt
    record.type_of_requisition = RequisitionRecord.REQUISITION_PEOPLE
    record.save()
    return record


def setup_service_requisition(service):
    """ Make service requisition fulfillable """
    service.is_open_for_ordering = True
    service.save()

    record = RequisitionRecord()
    record.affected_events = service.events.all()
    record.type_of_requisition = RequisitionRecord.REQUISITION_SERVICES
    record.save()
    return record


def enact_requisitoning_locks(all_events, requisition_records):
    requisitioned_events = {}
    for record in requisition_records:
        for event in record.affected_events:
            requisitioned_events[event.pk] = True
            event.silo = Event.REQUISITIONING_SILO
            event.is_locked = True
            event.save()

    for event in all_events:
        if (event.pk in requisitioned_events):
            continue

        event.silo = Event.PRODUCTION_SILO
        event.is_locked = True
        event.save()
    
    