from datetime import datetime, time, timedelta
import json
from typing import Optional, List, Tuple, Union
import uuid
from webook.arrangement.models import Event, EventSerie, Person, PlanManifest
from webook.graph_integration.graph_client.client_factory import (
    create_graph_service_client,
)

from msgraph.generated.models.event import Event as GraphEvent
from msgraph.generated.models.event_type import EventType as GraphEventType
from webook.graph_integration.models import GraphCalendar, SyncedEvent
from enum import Enum
from django.db.models import Q
from msgraph import GraphServiceClient
from msgraph.generated.models.calendar import Calendar
from webook.graph_integration.routines.mapping.single_event_mapping import (
    map_event_to_graph_event,
)
from asgiref.sync import sync_to_async
from webook.graph_integration.routines.mapping.repeating_event_mapping import (
    map_serie_to_graph_event,
)
from msgraph.generated.users.item.calendars.item.calendar_item_request_builder import (
    CalendarItemRequestBuilder,
)
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
from kiota_abstractions.base_request_configuration import RequestConfiguration
from django.conf import settings
import asyncio
import redlock
from django.conf import settings
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.users.item.events.item.instances.instances_request_builder import (
    InstancesRequestBuilder,
)

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


async def _get_instance_in_graph_repeating_event(
    calendar_item_request_builder: CalendarItemRequestBuilder,
    graph_event: GraphEvent,
    event: Event,
) -> Optional[GraphEvent]:
    """Given a GraphEvent and an Event, find the corresponding instance in the GraphEvent that should be
    a repeating event.

    Args:
        graph_service_client (GraphServiceClient): The GraphServiceClient to use.
        graph_event (GraphEvent): The GraphEvent to search in.
        event (Event): The Event to find the corresponding instance for.

    Returns:
        GraphEvent: The corresponding instance in the GraphEvent.

    Raises:
        ValueError: If the GraphEvent is not a repeating event.
        ValueError: If the instance cannot be found in the Graph event instances.
    """
    if graph_event.type != GraphEventType.SeriesMaster:
        raise ValueError("GraphEvent must be a repeating event")

    instances_request_configuration = RequestConfiguration(
        query_parameters=InstancesRequestBuilder.InstancesRequestBuilderGetQueryParameters(
            start_date_time=(datetime.now() - timedelta(7 * 4 * 3)).isoformat(),
            end_date_time=(datetime.now() + timedelta(7 * 4 * 3)).isoformat(),
        )
    )
    instances_request_configuration.headers.add(
        "Prefer", 'outlook.timezone="Europe/Oslo"'
    )

    instances = await calendar_item_request_builder.events.by_event_id(
        graph_event.id
    ).instances.get(instances_request_configuration)

    instance: Optional[GraphEvent] = next(
        (
            ge
            for ge in instances.value
            if (
                ge.type == GraphEventType.Occurrence
                or ge.type == GraphEventType.Exception
            )
            and datetime.strptime(
                ge.start.date_time.replace(".0000000", ""), "%Y-%m-%dT%H:%M:%S"
            ).date()
            == event.start.date()
        ),
        None,
    )

    if not instance:
        raise ValueError("Could not find instance in GraphEvent")

    return instance


async def _execute_sync_instructions(
    instructions: List[Tuple[Person, SyncedEvent, Operation]]
) -> List[SyncedEvent]:
    graph_service_client: GraphServiceClient = create_graph_service_client()

    request_configuration = RequestConfiguration()
    request_configuration.headers.add("Prefer", 'outlook.timezone="Europe/Oslo"')

    # We always want to process the repeating events (serie masters)
    instructions.sort(key=lambda instruction: instruction[1].event_type)
    print(instructions)

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
            if (
                synced_event.webook_event
                and synced_event.webook_event.association_type
                == Event.DEGRADED_FROM_SERIE
            ):
                # This event was formerly part of a serie, but has been degraded to a single event
                # There is no matching SyncedEvent yet for this event. Normally we would create the GraphEvent,
                # but for this case we already have one in Graph -- the instance of the serie.
                webook_serie: EventSerie = await sync_to_async(
                    lambda: synced_event.webook_event.associated_serie
                )()

                serie_synced_event = await webook_serie.synced_events.filter(
                    graph_calendar=synced_event.graph_calendar
                ).afirst()  # We want THIS calendar's instance of the serie.

                # If no serie = the person/resource is not added on serie level
                # We treat it as a "normal" event, makes sense in this scenario.
                if serie_synced_event:
                    graph_repeating_event = (
                        await calendar_request_builder.events.by_event_id(
                            serie_synced_event.graph_event_id
                        ).get(request_configuration)
                    )

                    matching_instance = await _get_instance_in_graph_repeating_event(
                        calendar_item_request_builder=calendar_request_builder,
                        graph_event=graph_repeating_event,
                        event=synced_event.webook_event,
                    )

                    # Now we do a PATCH request to update the instance with the new values.
                    resultant_event = await calendar_request_builder.events.by_event_id(
                        matching_instance.id
                    ).patch(mapped_graph_event, request_configuration)

                    synced_event.graph_event_id = resultant_event.id

            if not synced_event.graph_event_id:
                resultant_event: GraphEvent = (
                    await calendar_request_builder.events.post(
                        mapped_graph_event, request_configuration
                    )
                )
                synced_event.graph_event_id = resultant_event.id

            synced_event.event_hash = synced_event.calendar_item.hash_key()
            synced_event.state = SyncedEvent.SYNCED

            if synced_event.event_type == SyncedEvent.REPEATING:
                graph_serie = await calendar_request_builder.events.by_event_id(
                    synced_event.graph_event_id
                ).get(request_configuration)

                exception_events = (
                    synced_event.webook_event_serie.associated_events.filter(
                        association_type=Event.DEGRADED_FROM_SERIE
                    )
                    .select_related("arrangement")
                    .select_related("arrangement__location")
                    .prefetch_related("people")
                )

                async for exception_event in exception_events:
                    matching_instance: GraphEvent = (
                        await _get_instance_in_graph_repeating_event(
                            calendar_item_request_builder=calendar_request_builder,
                            graph_event=graph_serie,
                            event=exception_event,
                        )
                    )

                    await calendar_request_builder.events.by_event_id(
                        matching_instance.id
                    ).patch(
                        body=await map_event_to_graph_event(exception_event),
                        request_configuration=request_configuration,
                    )

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
        print("Saving event", synced_event.graph_event_id, synced_event.event_type)
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
    # Ignore those without arrangement - they are the ones used for collision analysis and are to be considered invisible.
    serie_manifests = PlanManifest.objects.filter(event_series__isnull=False)

    if future_only:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = events.filter(start__gte=today)
        serie_manifests = serie_manifests.filter(
            start_date__gte=today
        )  # TODO: Consider further...

    for event in events:
        # It is possible for an event to be considered need-to-sync and it's parent serie not to be
        # In this case, we push the serie in.
        if event.associated_serie and event.associated_serie not in serie_manifests:
            serie_manifests = serie_manifests | PlanManifest.objects.filter(
                id=event.associated_serie.id
            )
            continue
        if event.serie and event.serie not in serie_manifests:
            serie_manifests = serie_manifests | PlanManifest.objects.filter(
                id=event.serie.id
            )

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
            (
                item.synced_events.filter(graph_calendar__person__in=persons)
                if persons
                else item.synced_events
            )
            .select_related("webook_event_serie")
            .prefetch_related("webook_event_serie__associated_events")
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
            .users.by_user_id(
                person.social_provider_email
            )
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

    try:
        await client.users.by_user_id(
            person.social_provider_email
        ).calendars.by_calendar_id(calendar.calendar_id).delete()
    except ODataError as err:
        if err.response_status_code != 404:
            raise err

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
        persons = [
            p for p in persons if p.calendar_sync_enabled and p.social_provider_id
        ]

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
