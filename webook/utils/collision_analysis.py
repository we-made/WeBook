from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Union
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


Range = namedtuple('Range', ['start', 'end'])
RoomCalendar = namedtuple('RoomCalendar', [ 'room', 'events' ])


def analyze_collisions(events: Union[List[dict], dict]) -> Union[List[CollisionRecord], CollisionRecord]:
    """
        Analyze a list of events, or a single event for collisions. Returns a list of CollisionRecord if analyzing
        multiple events, or a single CollisionRecord if only one event.
    """

    earliest_start = min ( map(lambda event: event.start, events) )
    latest_end = max ( map(lambda event: event.end, events) )

    room_calendars = {}
    room_ids = []

    for event in events:
        for room_id in event.rooms:
            if room_id not in room_ids:
                room_ids.append(room_id)

    exclusive_rooms = Room.objects.filter(pk__in=room_ids)
    for room in exclusive_rooms:
        room_calendars[room.id] = RoomCalendar (room, list(room.event_set.filter( Q(start__lte = latest_end) & Q(end__gte = earliest_start))))

    return _analyze_multiple_events(events, room_calendars, room_ids)
    

def _analyze_multiple_events(events: List[dict], rooms: dict, room_ids: List[int]) -> List[CollisionRecord]:
    """ Analyze a sequence of given events, and see if they collide with any other existing events """
    records = []

    for event in events:
        utc = pytz.UTC
        event.start = utc.localize(event.start)
        event.end = utc.localize(event.end)
        exclusive_room_ids = [value for value in room_ids if value in event.rooms]
        for exlusive_room_id in exclusive_room_ids:
            room_calendar = rooms[exlusive_room_id]
            for r_event in room_calendar.events:
                if (r_event.start < event.end and r_event.end > event.start):
                    records.append(CollisionRecord(
                        event_a_title=event.title,
                        event_a_start=event.start,
                        event_a_end=event.end,
                        event_b_title=r_event.title,
                        event_b_start=r_event.start,
                        event_b_end=r_event.end,
                        contested_resource_id=room_calendar.room.id,
                        contested_resource_name=room_calendar.room.name,
                    ))
    
    return records