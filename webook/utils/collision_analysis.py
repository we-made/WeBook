from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import pytz
from django.db.models import Q

from webook.arrangement.models import Arrangement, Event, EventSerie, Room


@dataclass
class CollisionRecord:
    event_a_title: str
    event_a_start: datetime
    event_a_end: datetime
    event_b_title: str
    event_b_start: datetime
    event_b_end: datetime
    contested_resource_id: int
    contested_resource_name: str
    is_rigging: bool = False
    is_resolution: bool = False
    my_serie_position_hash: Optional[str] = None
    parent_serie_position_hash: Optional[str] = None


RoomCalendar = namedtuple("RoomCalendar", ["room", "events"])


def explode_rigging_events(event_to_explode: Event):
    """
    Explode the rigging events of a given event -- manifesting them for collision analysis

    Returns a dict containing two keys, before and after, each key may have a value of an event, which is the exploded
    rigging event. If the value is none, then there is no properly configured rigging event for this position relative to the given event.
    """
    pass


def analyze_collisions(
    events: Union[List[dict], dict],
    annotate_events: bool = True,
    ignore_serie_pk: Optional[int] = None,
) -> Union[List[CollisionRecord], CollisionRecord]:
    """
    Analyze a list of events, or a single event for collisions. Returns a list of CollisionRecords.
    If annotate_events is True then the items in the event list will have a new attribute set; is_collision.
    If true then the event is in a collision with another event.
    """

    if len(events) == 0:
        return []

    earliest_start = min(map(lambda event: event.start, events))
    latest_end = max(map(lambda event: event.end, events))

    room_calendars = {}
    room_ids = []

    for event in events:
        if annotate_events:
            event.is_collision = False

        for room_id in event.rooms:
            if room_id not in room_ids:
                room_ids.append(room_id)

    ignore_serie_criterion = ~Q(pk__in=[])
    if ignore_serie_pk:
        ignore_serie_criterion = ~Q(serie_id=ignore_serie_pk)

    exclusive_rooms = Room.objects.filter(Q(pk__in=room_ids) & Q(is_exclusive=True))
    room_ids = [room.id for room in exclusive_rooms]
    for room in exclusive_rooms:
        room_calendars[room.id] = RoomCalendar(
            room,
            list(
                room.event_set.filter(
                    Q(start__lte=latest_end)
                    & Q(end__gte=earliest_start)
                    & ignore_serie_criterion
                )
            ),
        )

    return _analyze_multiple_events(events, room_calendars, room_ids)


def _analyze_multiple_events(
    events: List[dict], rooms: dict, room_ids: List[int]
) -> List[CollisionRecord]:
    """Analyze a sequence of given events, and see if they collide with any other existing events"""
    records = []

    for event in events:
        utc = pytz.UTC
        if event.start.tzinfo is None:
            event.start = utc.localize(event.start)
        if event.end.tzinfo is None:
            event.end = utc.localize(event.end)
        exclusive_room_ids = [value for value in room_ids if value in event.rooms]
        for exlusive_room_id in exclusive_room_ids:
            room_calendar = rooms[int(exlusive_room_id)]
            for r_event in room_calendar.events:
                if r_event.start < event.end and r_event.end > event.start:
                    records.append(
                        CollisionRecord(
                            event_a_title=event.title,
                            event_a_start=event.start,
                            event_a_end=event.end,
                            event_b_title=r_event.title,
                            event_b_start=r_event.start,
                            event_b_end=r_event.end,
                            contested_resource_id=room_calendar.room.id,
                            contested_resource_name=room_calendar.room.name,
                            my_serie_position_hash=event.serie_positional_hash,
                            parent_serie_position_hash=event.sph_of_root_event,
                            is_rigging=event.is_rigging
                            if hasattr(event, "is_rigging")
                            else None,
                        )
                    )
                    if hasattr(event, "is_collision"):
                        event.is_collision = True

    return records
