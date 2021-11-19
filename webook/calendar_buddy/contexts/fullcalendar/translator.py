from ....calendar_buddy.mediative.mediative_event import MediativeEvent
from ....calendar_buddy.mediative.mediative_resource import MediativeResource

from ....calendar_buddy.contexts.fullcalendar.models import Event, Resource

def _set_defaults_on_dict(dict_to_set_defaults_on: dict(), defaults_to_set) -> dict:
    for key in defaults_to_set:
        dict_to_set_defaults_on.setdefault(key, defaults_to_set[key])
    return dict_to_set_defaults_on


def translate_event (mediative_event: MediativeEvent, defaults: dict()) -> Event:
    """ Translate from a mediative event to a FullCalendar event object """

    mediative_event.kwargs = _set_defaults_on_dict(mediative_event.kwargs, defaults)

    event = Event(
        id=mediative_event.id,
        title=mediative_event.title,
        groupId=mediative_event.kwargs["groupId"],
        allDay=mediative_event.kwargs["allDay"],
        start=mediative_event.kwargs["start"],
        end=mediative_event.kwargs["end"],
        startStr=mediative_event.kwargs["startStr"],
        endStr=mediative_event.kwargs["endStr"],
        url=mediative_event.kwargs["url"],
        classNames=mediative_event.kwargs["classNames"],
        editable=mediative_event.kwargs["editable"],
        startEditable=mediative_event.kwargs["startEditable"],
        durationEditable=mediative_event.kwargs["durationEditable"],
        resourceEditable=mediative_event.kwargs["resourceEditable"],
        display=mediative_event.kwargs["display"],
        overlap=mediative_event.kwargs["overlap"],
        constraint=mediative_event.kwargs["constraint"],
        backgroundColor=mediative_event.kwargs["backgroundColor"],
        borderColor=mediative_event.kwargs["borderColor"],
        textColor=mediative_event.kwargs["textColor"],
        extendedProps=mediative_event.kwargs["extendedProps"],
        source=mediative_event.kwargs["source"],
    )

    return event


def translate_resource(mediative_resource: MediativeResource, defaults: dict()) -> Resource:
    """ Translate from a mediative resource to a FullCalendar resource object """

    mediative_resource.kwargs = _set_defaults_on_dict(mediative_resource.kwargs, defaults)

    resource = Resource(
        id=mediative_resource.id,
        title=mediative_resource.title,
        extendedProps=mediative_resource.kwargs["extendedProps"],
        eventConstraint=mediative_resource.kwargs["eventConstraint"],
        eventOverlap=mediative_resource.kwargs["eventOverlap"],
        eventAllow=mediative_resource.kwargs["eventAllow"],
        eventBackgroundColor=mediative_resource.kwargs["eventBackgroundColor"],
        eventBorderColor=mediative_resource.kwargs["eventBorderColor"],
        eventTextColor=mediative_resource.kwargs["eventTextColor"],
        eventClassNames=mediative_resource.kwargs["eventClassNames"],
    )

    return resource

