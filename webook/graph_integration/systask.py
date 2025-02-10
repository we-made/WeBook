from argparse import ArgumentError
import asyncio
from webook.arrangement.models import Person, Event
from webook.graph_integration.models import GraphCalendar
from webook.systask.tasklib import systask
import webook.graph_integration.routines.calendar_sync as cal_sync
from webook.systask.task_manager_factory import create_task_manager
from webook.users.models import User


@systask
def synchronize_user_calendar(user_pk: int):
    """
    Synchronize a WeBook calendar for a given user in Graph / Outlook.
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


@systask
def subscribe_person_to_webook_calendar(person_pk: int):
    """
    Subscribe to the WeBook personal calendar for the given user, creating the calendar in Graph / Outlook and WeBook.
    """
    person = Person.objects.get(pk=person_pk)

    _: GraphCalendar = asyncio.run(cal_sync.subscribe_person_to_webook_calendar(person))

    task_manager = create_task_manager()
    task_manager.enqueue_task(
        task_name="synchronize_user_calendar",
        task_args={"user_pk": person.user_set.first().pk},
        task_kwargs={},
    )


@systask
def unsubscribe_person_from_webook_calendar(person_pk: int):
    """
    Unsubscribe from the WeBook personal calendar for the given user, deleting the calendar in Graph / Outlook and WeBook.
    """
    person: Person = Person.objects.get(pk=person_pk)
        
    if not person:
        raise ArgumentError(f"Person by ID '{person_pk}' does not exist")

    asyncio.run(cal_sync.unsubscribe_person_from_webook_calendar(person))


@systask
def synchronize_all_user_calendars():
    """
    Synchronize all WeBook calendars for all users in Graph / Outlook.
    """
    for user in User.objects.all():
        synchronize_user_calendar(user.pk)


@systask
def synchronize_event_to_graph(event_pk: int):
    """
    Synchronize a WeBook event to Graph / Outlook.
    """
    event = Event.objects.get(pk=event_pk)

    if not event:
        raise ArgumentError(f"Event by ID '{event_pk}' does not exist")

    return cal_sync.synchronize_calendars(
        future_only=False,
        event_ids=[event_pk],
        dry_run=False,
    )
