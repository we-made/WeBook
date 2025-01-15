from datetime import datetime, time
import json
from typing import Optional, List, Tuple, Union
import uuid
from webook.arrangement.models import Event, EventSerie, Person, PlanManifest
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

from webook.graph_integration.routines.mapping.repeating_event_mapping import (
    map_serie_to_graph_event,
)
from msgraph.generated.users.item.calendars.item.calendar_item_request_builder import (
    CalendarItemRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration
from django.conf import settings
import asyncio
import redlock
from django.conf import settings
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter

if not settings.REDIS_URL:
    raise ValueError("REDIS_URL is not set in settings")

__redlock_factory = redlock.RedLockFactory(
    connection_details=[
        {"host": settings.REDIS_URL.replace("redis://", "").split(":")[0]}
    ]
)


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


async def _execute_sync_instructions(
    instructions: List[Tuple[Person, SyncedEvent, Operation]]
) -> List[SyncedEvent]:
    graph_service_client: GraphServiceClient = create_graph_service_client()

    request_configuration = RequestConfiguration()
    request_configuration.headers.add("Prefer", 'outlook.timezone="Europe/Oslo"')

    for person, synced_event, operation in instructions:
        if operation == Operation.IGNORE:
            continue

        mapped_graph_event: GraphEvent = None

        if synced_event.event_type == synced_event.REPEATING:
            mapped_graph_event = await map_serie_to_graph_event(
                synced_event.webook_event_serie
            )
        else:
            mapped_graph_event = await map_event_to_graph_event(
                synced_event.webook_event
            )

        calendar_request_builder: CalendarItemRequestBuilder = (
            graph_service_client.users.by_user_id(
                person.social_provider_email
            ).calendars.by_calendar_id(synced_event.graph_calendar.calendar_id)
        )

        print("calendar_id|" + synced_event.graph_calendar.calendar_id)

        if operation == Operation.CREATE:
            resultant_event: GraphEvent = await calendar_request_builder.events.post(
                mapped_graph_event, request_configuration
            )
            synced_event.graph_event_id = resultant_event.id
            synced_event.event_hash = synced_event.calendar_item.hash_key()
            synced_event.state = SyncedEvent.SYNCED
            print("Created event", resultant_event.id)
        elif operation == Operation.UPDATE:
            await calendar_request_builder.events.by_event_id(
                synced_event.graph_event_id
            ).patch(mapped_graph_event, request_configuration)

            synced_event.event_hash = synced_event.calendar_item.hash_key()
            print("Updated event", synced_event.graph_event_id)
        elif operation == Operation.DELETE:
            mapped_graph_event.is_cancelled = True

            await calendar_request_builder.events.by_event_id(
                synced_event.graph_event_id
            ).patch(mapped_graph_event, request_configuration)

            synced_event.state = SyncedEvent.DELETED
            print("Deleted event", synced_event.graph_event_id)

        synced_event.synced_counter += 1
        await synced_event.asave()

    return list(map(lambda instruction: instruction[1], instructions))


def _get_events_matching_criteria(
    future_only: bool,
    persons: Optional[List[Person]],
    event_ids: Optional[List[int]] = None,
    serie_ids: Optional[List[int]] = None,
) -> List[Union[Event, EventSerie]]:
    """Get events for synchronization that match the given criteria.

    Args:
        future_only (bool): If True, only return events that are in the future.
        persons (Optional[List[Person]]): Persons to filter events by.
        event_ids (Optional[List[int]]): Event IDs to filter by.
    """

    events = (
        Event.objects.filter(serie__isnull=True)
        .prefetch_related("synced_events")
        .prefetch_related("people")
        .prefetch_related("rooms")
        .prefetch_related("arrangement")
        .prefetch_related("arrangement__location")
    )
    serie_manifests = PlanManifest.objects.all()

    if future_only:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = events.filter(start__gte=today)
        serie_manifests = serie_manifests.filter(
            start_date__gte=today
        )  # TODO: Consider further...

    if event_ids:
        events = events.filter(id__in=event_ids)

        if not serie_ids:
            serie_manifests = serie_manifests.none()

    if serie_ids:
        serie_manifests = serie_manifests.filter(id__in=serie_ids)

        if not event_ids:
            events = events.none()

    if persons:
        # Gets any events that have at least one person in the persons list
        events = events.filter(people__in=persons)
        serie_manifests = serie_manifests.filter(people__in=persons)

    events = events.all()
    event_series = (
        EventSerie.objects.filter(serie_plan_manifest__in=serie_manifests)
        .prefetch_related("events")
        .select_related("arrangement")
        .select_related("arrangement__location")
        .all()
    )

    return [*list(events), *list(event_series)]


def _calculate_instructions(
    calendar_items: List[Union[Event, EventSerie]], persons: List[Person] = []
) -> List[Tuple[Person, SyncedEvent, Operation]]:
    """Given a list of events and persons (optional), calculate what operations need to be performed to synchronize the events
    to Outlook.

    Args:
        events (List[Event]): List of events to synchronize.
        persons (List[Person], optional): List of persons to synchronize. Defaults to [].
                                          If empty, all persons with calendar sync enabled will be used.
    """
    instructions: List[Tuple[Person, SyncedEvent, Operation]] = []

    if not calendar_items:
        raise ValueError("Provided list of events is empty.")

    for item in calendar_items:
        synced_events = (
            item.synced_events.filter(graph_calendar__person__in=persons).all()
            if persons
            else item.synced_events.all()
        )

        for synced_event in synced_events:
            if (
                synced_event.webook_event
                if synced_event.event_type == synced_event.SINGLE
                else synced_event.webook_event_serie
            ).is_archived:
                instructions.append(
                    (synced_event.graph_calendar.person, synced_event, Operation.DELETE)
                )
                continue

            if synced_event.is_in_sync:
                continue

            instructions.append(
                (synced_event.graph_calendar.person, synced_event, Operation.UPDATE)
            )
            print(
                "Adding update instruction",
                synced_event.graph_event_id,
                synced_event.graph_calendar.person.id,
            )

        # If the consumer has specified persons, we should only sync the event for those persons
        # Otherwise, we should sync the event for all persons associated with the event. It's important that we don't use the "all" persons
        # as this would generate instructions that include all persons in the system, not just the persons associated with the event. That's a bad day.

        people_qs = (
            item.people if isinstance(item, Event) else item.serie_plan_manifest.people
        )

        for person in (
            people_qs.all()
            if not persons
            else people_qs.filter(pk__in=[person.pk for person in persons]).all()
        ):
            if not item.synced_events.filter(graph_calendar__person=person).exists():
                try:
                    calendar = GraphCalendar.objects.get(person=person)
                except GraphCalendar.DoesNotExist:
                    calendar = None

                instructions.append(
                    (
                        person,
                        SyncedEvent(
                            event_type=(
                                SyncedEvent.SINGLE
                                if isinstance(item, Event)
                                else SyncedEvent.REPEATING
                            ),
                            webook_event=item if isinstance(item, Event) else None,
                            webook_event_serie=(
                                item if isinstance(item, EventSerie) else None
                            ),
                            graph_calendar=calendar,
                            event_hash=item.hash_key(),
                        ),
                        Operation.CREATE,
                    )
                )
                print("Adding create instruction", item.id, person.id)

    return instructions


async def subscribe_person_to_webook_calendar(person: Person) -> GraphCalendar:
    """Subscribe a person to a WeBook calendar in Graph / Outlook."""

    with __redlock_factory.create_lock(person.social_provider_email, retry_times=3):
        if not person.social_provider_id:
            raise ValueError("Person does not have a social provider ID")

        if await GraphCalendar.objects.filter(person=person).aexists():
            raise ValueError("Person is already subscribed to a calendar")

        result = (
            await create_graph_service_client()
            .users.by_user_id(person.social_provider_email)
            .calendars.post(
                Calendar(name=settings.APP_TITLE + " - " + person.full_name)
            )
        )

        graph_calendar_representation = GraphCalendar(
            person_id=person.id, name=result.name, calendar_id=result.id
        )
        await graph_calendar_representation.asave()

        person.calendar_sync_enabled = True
        await person.asave()

        return graph_calendar_representation


async def unsubscribe_person_from_webook_calendar(person: Person) -> None:
    """Unsubscribe from the WeBook personal calendar for the given user."""
    client: GraphServiceClient = create_graph_service_client()
    try:
        calendar = await GraphCalendar.objects.aget(person=person)
    except GraphCalendar.MultipleObjectsReturned:
        calendar = await GraphCalendar.objects.filter(person=person).afirst()

    if not calendar:
        raise ValueError(f"Person by ID '{person.id}' is not subscribed to a calendar")

    await client.users.by_user_id(
        person.social_provider_email
    ).calendars.by_calendar_id(calendar.calendar_id).delete()

    await calendar.adelete()

    person.calendar_sync_enabled = False
    await person.asave()


def synchronize_calendars(
    future_only: bool = True,
    persons: Optional[List[Person]] = None,
    event_ids: Optional[List[int]] = None,
    serie_ids: Optional[List[int]] = None,
    dry_run: bool = False,
):
    if persons:
        # Sanity check the provided persons - we can only sync calendars for persons that have calendar sync enabled and a social provider ID
        if not all([person.calendars.exists() for person in persons]):
            raise ValueError(
                "Not all persons have calendar sync enabled. Please enable calendar sync for all persons."
            )
        if not all([person.social_provider_id for person in persons]):
            raise ValueError(
                "Not all persons have a social provider ID. Please set a social provider ID for all persons."
            )

    calendar_items: List[Union[Event, PlanManifest]] = _get_events_matching_criteria(
        future_only, persons, event_ids, serie_ids
    )

    if not calendar_items:
        print("No events to sync")
        return []

    persons: List[Person] = (
        persons
        or Person.objects.filter(
            Q(social_provider_id__isnull=False) & Q(calendar_sync_enabled=True)
        ).all()
    )

    # We need to ensure that we only have one instance of the sync_calendars lock running at any given time
    # If an event is saved two times in quick succession, we don't want to run the sync twice, possibly creating duplicate events in the calendar
    with __redlock_factory.create_lock(
        "sync_calendars", retry_times=3, retry_delay=200
    ):
        instructions: List[Tuple[Person, SyncedEvent, Operation]] = (
            _calculate_instructions(calendar_items, persons)
        )

        if not instructions:
            return []

        if dry_run:
            print("dry run, returning instructions")
            return instructions

        print("executing instructions", len(instructions))

        synced_events = asyncio.run(_execute_sync_instructions(instructions))

        print("Done syncing events")

        return [
            {
                "id": se.id,
                "webook_event_id": se.webook_event.id if se.webook_event else None,
                "webook_event_serie_id": (
                    se.webook_event_serie.id if se.webook_event_serie else None
                ),
                "graph_event_id": se.graph_event_id,
                "graph_calendar_id": se.graph_calendar.id,
                "event_hash": se.event_hash,
                "synced_counter": se.synced_counter,
                "state": se.state,
                "event_type": se.event_type,
            }
            for se in synced_events
        ]
