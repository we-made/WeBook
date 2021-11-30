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


def get_base_resource_standard() -> dict:
    """
        Get the base resource standard.
        This covers the entire fullcalendar event model

        :return: Returns a dict, containing the base resource standards
        :rtype: dict
    """
    return {
        "extendedProps": [],
        "eventConstraint": None,
        "eventOverlap": False,
        "eventAllow": False,
        "eventBackgroundColor": "",
        "eventBorderColor": "",
        "eventTextColor": "",
        "eventClassNames": []
    }
