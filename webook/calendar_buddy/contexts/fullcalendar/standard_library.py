from datetime import datetime
from .models import EventDisplay


def get_base_event_standard() -> dict:
    """
        Get the base event standard.
        This covers the entire fullcalendar event model
        
        :return: Returns a dict, containing the base event standards
        :rtype: dict
    """
    return {
        "groupId": "",
        "allDay": False,
        "start": datetime.now(),
        "end": datetime.now(),
        "startStr": "",
        "endStr": "",
        "url": "",
        "classNames": [],
        "editable": False,
        "startEditable": False,
        "durationEditable": False,
        "resourceEditable": False,
        "display": EventDisplay.AUTO,
        "overlap": None,
        "constraint": None,
        "backgroundColor": "",
        "borderColor": "",
        "textColor": "",
        "extendedProps": [],
        "source": None
    }
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


def get_base_resource_standard() -> dict:
    """
        Get the base resource standard.
        This covers the entire fullcalendar event model

        :return: Returns a dict, containing the base resource standards
        :rtype: dict
    """
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
