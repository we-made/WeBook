
from datetime import datetime
import json

class MediativeEvent:
    """
        MediativeEvent is the bare minimum an event type for a context must implement. 
        It serves as the "common tongue" that CalendarBuddy understands, and can work with.
        The kwargs attribute allows you to specify extra attributes, and through the use of translators
        in your context implementation you should be able to build a fully fledged event that matches
        the context domain.
    """

    def __init__(self, id: str, title: str, start: datetime, end: datetime, **kwargs):
        self.id = id
        self.title = title
        self.start = start
        self.end = end
        self.kwargs = kwargs
