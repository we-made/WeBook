import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class EventDTO:
    title: str
    start: datetime
    end: datetime

    title_en: str = ""

    rooms: list = field(default_factory=list)
    people: List[int] = field(default_factory=list)
    display_layouts: list = field(default_factory=list)
    arrangement_id: int = None
    expected_visitors: int = None
    color: str = None
    sequence_guid: str = None
    ticket_code: str = None

    is_resolution: bool = False
    
