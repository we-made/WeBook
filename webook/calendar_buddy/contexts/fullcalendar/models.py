from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
import json
from json import JSONEncoder


class EventDisplay(Enum):
    """
        Please refer to: https://fullcalendar.io/docs/eventDisplay
        This mirrors FullCalendar (V5) event display
    """
    AUTO = 0
    BLOCK = 1
    LIST_ITEM = 2
    BACKGROUND = 3
    INVERSE_BACKGROUND = 4
    NONE = 5


@dataclass
class BusinessHours:
    """
        Please refer to: https://fullcalendar.io/docs/businessHours
        This mirrors FullCalendar (V5) business hours
    """

    startTime: time
    endTime: time

    daysOfWeek: list()


@dataclass
class Event:
    """
        Please refer to: https://fullcalendar.io/docs/event-object
        This mirrors FullCalendar (V5) event definition
    """

    id: str
    groupId: str
    allDay: bool
    start: datetime
    end: datetime
    # ISO8601 representation of start date
    startStr: str
    # ISO8601 representation of end date
    endStr: str
    title: str
    url: str
    classNames: list()
    editable: bool
    startEditable: bool
    durationEditable: bool
    resourceEditable: bool
    display: EventDisplay
    overlap: bool
    constraint: BusinessHours
    backgroundColor: str
    borderColor: str
    textColor: str
    extendedProps: list()
    source: str


@dataclass
class Resource:
    """
        Please refer to: https://fullcalendar.io/docs/resource-object
        This mirrors FullCalendar (V5)
    """

    id: str
    title: str
    extendedProps: list()
    eventConstraint: BusinessHours
    eventOverlap: bool
    eventAllow: bool
    eventBackgroundColor: str
    eventBorderColor: str
    eventTextColor: str
    eventClassNames: str
