from argparse import ArgumentError
from datetime import datetime
from typing import List, Tuple
from celery import shared_task
import uuid
from webook import logger
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
import webook.graph_integration.routines.calendar_sync as cal_sync
from webook.users.models import User
import asyncio


class Operation(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    IGNORE = "ignore"


@shared_task(name="subscribe_person_to_webook_calendar")
def subscribe_person_to_webook_calendar(person_pk: int):
    """
    Subscribe to the WeBook personal calendar for the given user, if it is not already subscribed.
    Will subsequently trigger a full user cal synchronization to the calendar in Graph / Outlook.
    """
    print("subscribe_person_to_webook_calendar", person_pk)

    person = Person.objects.get(pk=person_pk)

    _: GraphCalendar = asyncio.run(cal_sync.subscribe_person_to_webook_calendar(person))

    synchronize_user_calendar.delay(person.user_set.first().pk)


@shared_task(name="unsubscribe_person_from_webook_calendar")
def unsubscribe_person_from_webook_calendar(person_pk: int):
    """
    Unsubscribe from the WeBook personal calendar for the given user, deleting the calendar in Graph / Outlook and WeBook.
    """
    person: Person = Person.objects.get(pk=person_pk)

    if not person:
        raise ArgumentError(f"Person by ID '{person_pk}' does not exist")

    asyncio.run(cal_sync.unsubscribe_person_from_webook_calendar(person))


@shared_task(name="synchronize_user_calendar")
def synchronize_user_calendar(user_pk: int):
    """
    Synchronize a WeBook calendar for a given user in Graph / Outlook.
    This will populate all future events, and series, in the calendar of that user.
    """
    try:
        _ = User.objects.get(id=user_pk)
    except User.DoesNotExist:
        raise ArgumentError(f"User by ID '{user_pk}' does not exist")

    return cal_sync.synchronize_calendars(
        future_only=True,
        persons=Person.objects.filter(user__id=user_pk).all(),
        dry_run=False,
    )


@shared_task(name="synchronize_event_to_graph")
def synchronize_event_to_graph(event_pk: int):
    """
    Synchronize a specific WeBook event to Graph / Outlook.
    This will populate that event in the calendars of all users that are associated with the event.
    """
    event = Event.objects.get(pk=event_pk)

    if not event:
        raise ArgumentError(f"Event by ID '{event_pk}' does not exist")

    return cal_sync.synchronize_calendars(
        future_only=False,
        event_ids=[event_pk],
        dry_run=False,
    )


# @shared_task
# def synchronize_all_calendars(future_events_only: bool = True):
#     """Synchronize all calendars for all users in Graph / Outlook."""
#     # Get all events that are in the future if future_events_only is True
#     # And if they have one person or more associated with them
#     events = (
#         (
#             Event.objects.filter(start__gte=datetime.now())
#             if future_events_only
#             else Event.objects.all()
#         )
#         .filter(people__isnull=False)
#         .prefetch_related("synced_events")
#         .prefetch_related("people")
#     ).all()

#     instructions: List[Tuple[SyncedEvent, Operation]] = []

#     for event in events:
#         synced_events = (
#             event.synced_events.all()
#         )  # One event can be synced to multiple calendars

#         persons = event.people.filter(
#             Q(social_provider_id__isnull=False) & Q(calendar_sync_enabled=True)
#         ).all()
#         events_for_person_dict = {}

#         for synced_event in synced_events:
#             events_for_person_dict[synced_event.graph_calendar.person] = synced_event

#             if synced_event.is_in_sync():
#                 continue

#             instructions.append((synced_event, Operation.UPDATE))

#         for person in persons:
#             if person not in events_for_person_dict:
#                 calendar = GraphCalendar.objects.get(person=person)
#                 if calendar is None:
#                     logger.error(
#                         f"Person by ID '{person.pk}' is not subscribed to a calendar"
#                     )
#                     continue
#                 instructions.append(
#                     (
#                         SyncedEvent(
#                             webook_event=event,
#                             graph_calendar=GraphCalendar.objects.get(person=person),
#                         ),
#                         Operation.CREATE,
#                     )
#                 )

#     synced_events_referring_archived_events = SyncedEvent.objects.filter(
#         Q(webook_event__is_archived=True) & Q(webook_event__start__gte=datetime.now())
#     ).all()

#     for synced_event in synced_events_referring_archived_events:
#         instructions.append((synced_event, Operation.DELETE))

#     sync_events(instructions)
