from datetime import datetime
from .models import EventDisplay


def get_base_event_standard():
    event_standard = dict()
    event_standard["groupId"] = ""
    event_standard["allDay"] = False
    event_standard["start"] = datetime.now()
    event_standard["end"] = datetime.now()
    event_standard["startStr"] = ""
    event_standard["endStr"] = ""
    event_standard["url"] = ""
    event_standard["classNames"] = []
    event_standard["editable"] = False
    event_standard["startEditable"] = False
    event_standard["durationEditable"] = False
    event_standard["resourceEditable"] = False
    event_standard["display"] = EventDisplay.AUTO
    event_standard["overlap"] = None
    event_standard["constraint"] = None
    event_standard["backgroundColor"] = ""
    event_standard["borderColor"] = ""
    event_standard["textColor"] = ""
    event_standard["extendedProps"] = []
    event_standard["source"] = None
    return event_standard


def get_base_resource_standard():
    resource_standard = dict()
    resource_standard["extendedProps"] = []
    resource_standard["eventConstraint"] = None
    resource_standard["eventOverlap"] = False
    resource_standard["eventAllow"] = False
    resource_standard["eventBackgroundColor"] = ""
    resource_standard["eventBorderColor"] = ""
    resource_standard["eventTextColor"] = ""
    resource_standard["eventClassNames"] = []
    return resource_standard
