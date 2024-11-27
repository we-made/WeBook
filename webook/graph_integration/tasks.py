from argparse import ArgumentError
from datetime import datetime
from typing import List, Tuple
from celery import shared_task
from webook.arrangement.models import Event, Person
from webook.graph_integration.models import GraphCalendar, SyncedEvent
from enum import Enum
from django.db.models import Q
from webook.graph_integration.graph_client.client_factory import (
    create_graph_service_client,
)
from msgraph import GraphServiceClient
from msgraph.generated.models.calendar import Calendar
from django.conf import settings
from webook.users.models import User


class Operation(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    IGNORE = "ignore"


def sync_events(instructions: List[Tuple[SyncedEvent, Operation]]):
    client = create_graph_service_client()
    for instruction in instructions:
        synced_event, operation = instruction

        if operation == Operation.CREATE:
            pass
        elif operation == Operation.UPDATE:
            pass
        elif operation == Operation.DELETE:
            pass
        elif operation == Operation.IGNORE:
            pass


async def create_calendar(person_pk: int) -> GraphCalendar:
    """Create a WeBook calendar for a given user in Graph / Outlook."""
    client: GraphServiceClient = create_graph_service_client()

    person: Person = Person.objects.get(pk=person_pk)

    result = await client.users.by_user_id(person.social_provider_email).calendars.post(
        Calendar(name=settings.APP_TITLE + " - " + person.full_name)
    )

    graph_calendar_representation = GraphCalendar(
        person_id=person_pk, name=result.name, calendar_id=result.id
    )
    graph_calendar_representation.save()

    return graph_calendar_representation


@shared_task
def synchronize_user_calendar(user_pk: int):
    """Synchronize a WeBook calendar for a given user in Graph / Outlook."""
    user = User.objects.get(id=user_pk)
    if not user:
        raise ArgumentError(f"User by ID '{user_pk}' does not exist")
    if not user.person.exists():
        raise ArgumentError(f"Person for user by ID '{user_pk}' does not exist")

    person = user.person.get()

    if not person.social_provider_id:
        raise ArgumentError(
            f"Person by ID '{person.pk}' does not have a social provider ID"
        )
    if not person.calendar_sync_enabled:
        raise ArgumentError(
            f"Person by ID '{person.pk}' does not have calendar sync enabled"
        )

    calendar = GraphCalendar.objects.get(person=person)

    if not calendar:
        calendar = create_calendar(person.pk)

    events = (
        Event.objects.filter(persons__in=[person])
        .filter(start__gte=datetime.now())
        .prefetch_related("synced_events")
        .prefetch_related("persons")
    ).all()

    instructions: List[Tuple[SyncedEvent, Operation]] = []

    for event in events:
        synced_event = event.synced_events.filter(graph_calendar=calendar).first()

        if not synced_event:
            instructions.append(
                (
                    SyncedEvent(
                        webook_event=event,
                        graph_calendar=calendar,
                    ),
                    Operation.CREATE,
                )
            )

        if not synced_event.is_in_sync():
            instructions.append((synced_event, Operation.UPDATE))

    synced_events_referring_archived_events = SyncedEvent.objects.filter(
        Q(webook_event__is_archived=True) & Q(webook_event__start__gte=datetime.now())
    ).all()

    for synced_event in synced_events_referring_archived_events:
        instructions.append((synced_event, Operation.DELETE))

    sync_events(instructions)


@shared_task
def synchronize_all_calendars(future_events_only: bool = True):
    """Synchronize all calendars for all users in Graph / Outlook."""
    # Get all events that are in the future if future_events_only is True
    # And if they have one person or more associated with them
    events = (
        (
            Event.objects.filter(start__gte=datetime.now())
            if future_events_only
            else Event.objects.all()
        )
        .filter(persons__isnull=False)
        .prefetch_related("synced_events")
        .prefetch_related("persons")
    ).all()

    instructions: List[Tuple[SyncedEvent, Operation]] = []

    for event in events:
        synced_events = (
            event.synced_events.all()
        )  # One event can be synced to multiple calendars

        persons = event.persons.filter(
            Q(social_provider_id__isnull=False) & Q(calendar_sync_enabled=True)
        ).all()
        events_for_person_dict = {}

        for synced_event in synced_events:
            events_for_person_dict[synced_event.graph_calendar.person] = synced_event

            if synced_event.is_in_sync():
                continue

            instructions.append((synced_event, Operation.UPDATE))

        for person in persons:
            if person not in events_for_person_dict:
                calendar = GraphCalendar.objects.get(person=person)
                if calendar is None:
                    create_calendar(person.pk)
                instructions.append(
                    (
                        SyncedEvent(
                            webook_event=event,
                            graph_calendar=GraphCalendar.objects.get(person=person),
                        ),
                        Operation.CREATE,
                    )
                )

    synced_events_referring_archived_events = SyncedEvent.objects.filter(
        Q(webook_event__is_archived=True) & Q(webook_event__start__gte=datetime.now())
    ).all()

    for synced_event in synced_events_referring_archived_events:
        instructions.append((synced_event, Operation.DELETE))

    sync_events(instructions)
