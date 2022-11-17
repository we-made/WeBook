import time
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

import pytz
from django.utils import timezone as dj_timezone

from webook.utils.sph_gen import get_serie_positional_hash


@dataclass
class EventDTO:

    title: str
    start: datetime
    end: datetime

    id: Optional[int] = None
    title_en: str = ""

    rooms: list = field(default_factory=list)
    people: List[int] = field(default_factory=list)
    display_layouts: list = field(default_factory=list)
    arrangement_id: int = None
    expected_visitors: int = None
    color: str = None
    sequence_guid: str = None
    ticket_code: str = None

    before_buffer_title: str = None
    before_buffer_date: datetime = None
    before_buffer_date_offset: int = None
    before_buffer_start: time = None
    before_buffer_end: time = None

    after_buffer_title: str = None
    after_buffer_date: datetime = None
    after_buffer_date_offset: int = None
    after_buffer_start: time = None
    after_buffer_end: time = None

    associated_serie_id: int = None

    is_resolution: bool = False
    is_rigging: bool = False
    sph_of_root_event: Optional[str] = None
    serie_positional_hash: Optional[str] = None

    def generate_serie_positional_hash(self, serie_uuid) -> str:
        return get_serie_positional_hash(serie_uuid, self.title, self.start, self.end)

    def generate_rigging_events(self):
        _title_generators_per_position = {
            "before": lambda root_name: "Opprigging for " + root_name,
            "after": lambda root_name: "Nedrigging for " + root_name,
        }

        time_pairs: List[Tuple[datetime, datetime, int]] = [
            (
                self.before_buffer_title,
                self.before_buffer_date,
                self.before_buffer_start,
                self.before_buffer_end,
                self.before_buffer_date_offset,
            ),
            (
                self.after_buffer_title,
                self.after_buffer_date,
                self.after_buffer_start,
                self.after_buffer_end,
                self.after_buffer_date_offset,
            ),
        ]

        current_tz = pytz.timezone(str(dj_timezone.get_current_timezone()))

        rigging_events = {"root": self}

        root_event_rooms = self.rooms
        root_event_people = self.people

        is_before = True
        for title, date, start_time, end_time, date_offset in time_pairs:
            if start_time is None or end_time is None:
                # We need both start and end to generate a rigging event
                # Without both present there is really no point.
                is_before = False
                continue

            position_key = "before" if is_before else "after"
            is_before = False

            date = date or self.start

            offset: Optional[datetime] = (
                timedelta(days=date_offset) if date_offset else timedelta(days=0)
            )
            if position_key == "before":
                date = date - offset
            else:
                date = date + offset

            rigging_event = EventDTO(
                title=title or _title_generators_per_position[position_key](self.title),
                start=current_tz.localize(datetime.combine(date, start_time)),
                end=current_tz.localize(datetime.combine(date, end_time)),
            )

            rigging_event.arrangement_id = self.arrangement_id

            # We can not set rooms or people before the event has been saved -- unfortunately.
            rigging_event.rooms = root_event_rooms
            rigging_event.people = root_event_people

            rigging_events[position_key] = rigging_event

        return rigging_events
