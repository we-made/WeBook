from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Union

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


def _extrapolate_collidables(events: List[dict], by_rooms:List[Room]) -> Tuple[ List[Event], List[Room] ]:
    exclusive_rooms = map( lambda x: x.id, by_rooms )
    events_collidable = []

    rooms = []

    for event in events:
        for room in event.rooms:
            if room in exclusive_rooms:
                events_collidable.append(event)
                rooms.append(room)

    return (events_collidable, rooms)


def analyze_collisions(events: Union[List[dict], dict]) -> Union[List[CollisionRecord], CollisionRecord]:
    """
        Analyze a list of events, or a single event for collisions. Returns a list of CollisionRecord if analyzing
        multiple events, or a single CollisionRecord if only one event.
    """

    room_criterion_is_exclusive = Q(is_exclusive=True)
    rooms = Room.objects.filter( room_criterion_is_exclusive )
    
    if len(events) == 1:
        return _analyze_single_event(events[0], rooms)
    elif len(events) > 1:
        return _analyze_multiple_events(events, rooms)
    
    raise ValueError("No events")
    

def _analyze_single_event(event: dict, rooms: List[Room]) -> List[CollisionRecord]:
    pass

def _analyze_multiple_events(events: List[dict], rooms: List[Room]) -> List[CollisionRecord]:
    pass
