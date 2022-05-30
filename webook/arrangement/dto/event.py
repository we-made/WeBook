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
    
