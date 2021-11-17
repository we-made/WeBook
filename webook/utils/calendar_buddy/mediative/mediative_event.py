
from datetime import datetime
import json

class MediativeEvent:
    def __init__(self, id: str, title: str, start: datetime, end: datetime, **kwargs):
        self.id = id
        self.title = title
        self.start = start
        self.end = end
        self.kwargs = kwargs
