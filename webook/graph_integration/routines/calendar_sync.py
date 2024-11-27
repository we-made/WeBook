from datetime import datetime
from typing import Optional, List, Tuple
from webook.arrangement.models import Event, Person
from webook.graph_integration.graph_client.client_factory import (
    create_graph_service_client,
)
from msgraph.generated.models.event import Event as GraphEvent
from webook.graph_integration.models import GraphCalendar, SyncedEvent
from enum import Enum
from django.db.models import Q
from msgraph import GraphServiceClient
from msgraph.generated.models.calendar import Calendar
from webook.graph_integration.routines.mapping.single_event_mapping import (
    map_event_to_graph_event,
)

# from webook.graph_integration.routines.mapping.repeating_event_mapping import (
#     map_repeating_event_to_graph_event,
# )
from msgraph.generated.users.item.calendars.item.calendar_item_request_builder import (
    CalendarItemRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration
from django.conf import settings


class Operation(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"  # set event isCancelled = true in graph
    IGNORE = "ignore"


def create_calendar(person_pk: int) -> GraphCalendar:
    """Create a WeBook calendar for a given user in Graph / Outlook."""
    client: GraphServiceClient = create_graph_service_client()

    person: Person = Person.objects.get(pk=person_pk)

    result = client.users.by_user_id(person.social_provider_email).calendars.post(
        Calendar(name=settings.APP_TITLE + " - " + person.full_name)
    )

    graph_calendar_representation = GraphCalendar(
        person_id=person_pk, name=result.name, calendar_id=result.id
    )
    graph_calendar_representation.save()

    return graph_calendar_representation


def _execute_sync_instructions(
    instructions: List[Tuple[Person, SyncedEvent, Operation]]
):
    graph_service_client: GraphServiceClient = create_graph_service_client()

    request_configuration = RequestConfiguration()
    request_configuration.headers = {
        "Prefer": 'outlook.timezone="Europe/Oslo"',
    }

    for person, synced_event, operation in instructions:
        if operation == Operation.IGNORE:
            continue

        mapped_graph_event: GraphEvent = map_event_to_graph_event(
            synced_event.webook_event
        )

        calendar_request_builder: CalendarItemRequestBuilder = (
            graph_service_client.users.by_user_id(
                person.social_provider_email
            ).calendars.by_calendar_id(synced_event.graph_calendar.calendar_id)
        )

        if operation == Operation.CREATE:
            resultant_event: GraphEvent = calendar_request_builder.events.post(
                mapped_graph_event, request_configuration
            )
            synced_event.graph_event_id = resultant_event.id
            synced_event.event_hash = synced_event.webook_event.hash_key()
            synced_event.state = SyncedEvent.SYNCED
        elif operation == Operation.UPDATE:
            calendar_request_builder.events.by_event_id(
                synced_event.graph_event_id
            ).patch(mapped_graph_event, request_configuration)

            synced_event.event_hash = synced_event.webook_event.hash_key()
        elif operation == Operation.DELETE:
            mapped_graph_event.is_cancelled = True

            calendar_request_builder.events.by_event_id(
                synced_event.graph_event_id
            ).patch(mapped_graph_event, request_configuration)

            synced_event.state = SyncedEvent.DELETED

        synced_event.synced_counter += 1
        synced_event.save()


def _get_events_matching_criteria(
    future_only: bool, persons: Optional[List[Person]], event_ids: Optional[List[int]]
) -> List[Event]:
    """Get events for synchronization that match the given criteria.

    Args:
        future_only (bool): If True, only return events that are in the future.
        persons (Optional[List[Person]]): Persons to filter events by.
        event_ids (Optional[List[int]]): Event IDs to filter by.
    """

    events = Event.objects.prefetch_related("synced_events").prefetch_related("people")

    if future_only:
        events = events.filter(start__gte=datetime.now())

    if event_ids:
        events = events.filter(id__in=event_ids)

    if persons:
        # Gets any events that have at least one person in the persons list
        events = events.filter(people__in=persons)

    events = events.all()

    return events


def _calculate_instructions(
    events: List[Event], persons: List[Person] = []
) -> List[Tuple[Person, SyncedEvent, Operation]]:
    """Given a list of events and persons (optional), calculate what operations need to be performed to synchronize the events
    to Outlook.

    Args:
        events (List[Event]): List of events to synchronize.
        persons (List[Person], optional): List of persons to synchronize. Defaults to [].
                                          If empty, all persons with calendar sync enabled will be used.
    """
    instructions: List[Tuple[Person, SyncedEvent, Operation]] = []

    if not events:
        raise ValueError("Provided list of events is empty.")

    for event in events:
        synced_events = (
            event.synced_events.filter(graph_calendar__person__in=persons).all()
            if persons
            else event.synced_events.all()
        )

        for synced_event in synced_events:
            if synced_event.webook_event.is_archived:
                instructions.append(
                    (synced_event.graph_calendar.person, synced_event, Operation.DELETE)
                )
                continue

            if synced_event.is_in_sync:
                continue

            instructions.append(
                (synced_event.graph_calendar.person, synced_event, Operation.UPDATE)
            )

        # If the consumer has specified persons, we should only sync the event for those persons
        # Otherwise, we should sync the event for all persons associated with the event. It's important that we don't use the "all" persons
        # as this would generate instructions that include all persons in the system, not just the persons associated with the event. That's a bad day.
        for person in (
            event.people.all()
            if not persons
            else event.people.filter(pk__in=[person.pk for person in persons]).all()
        ):
            if not event.synced_events.filter(graph_calendar__person=person).exists():
                try:
                    calendar = GraphCalendar.objects.get(person=person)
                except GraphCalendar.DoesNotExist:
                    calendar = None

                instructions.append(
                    (
                        person,
                        SyncedEvent(
                            webook_event=event,
                            graph_calendar=calendar,
                            event_hash=event.hash_key(),
                        ),
                        Operation.CREATE,
                    )
                )

    return instructions


def synchronize_calendars(
    future_only: bool = True,
    persons: Optional[List[Person]] = None,
    event_ids: Optional[List[int]] = None,
    dry_run: bool = False,
):
    if persons:
        # Sanity check the provided persons - we can only sync calendars for persons that have calendar sync enabled and a social provider ID
        if not all([person.calendar_sync_enabled for person in persons]):
            raise ValueError(
                "Not all persons have calendar sync enabled. Please enable calendar sync for all persons."
            )
        if not all([person.social_provider_id for person in persons]):
            raise ValueError(
                "Not all persons have a social provider ID. Please set a social provider ID for all persons."
            )

    events: List[Event] = _get_events_matching_criteria(future_only, persons, event_ids)

    persons: List[Person] = (
        persons
        or Person.objects.filter(
            Q(social_provider_id__isnull=False) & Q(calendar_sync_enabled=True)
        ).all()
    )

    instructions: List[Tuple[Person, SyncedEvent, Operation]] = _calculate_instructions(
        events, persons
    )

    if dry_run:
        return instructions

    _execute_sync_instructions(instructions)
