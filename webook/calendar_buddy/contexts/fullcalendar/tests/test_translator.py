from webook.calendar_buddy.mediative.mediative_event import MediativeEvent
from webook.calendar_buddy.mediative.mediative_resource import MediativeResource
from webook.calendar_buddy.contexts.fullcalendar import translator, standard_library, models
from datetime import datetime
import pytest


def test_translate_event():
    mediative_event = MediativeEvent(
        id="1",
        title="event",
        start=datetime.now(),
        end=datetime.now(),
        groupId="1" # <-- **kwargs
    )

    result_of_translation = translator.translate_event(mediative_event, standard_library.get_base_event_standard())

    assert result_of_translation is not None
    assert type(result_of_translation) is models.Event
    assert result_of_translation.groupId == "1"


def test_translate_resource():
    mediative_resource = MediativeResource(
        id="1",
        title="resource",
        eventAllow=True
    )

    result_of_translation = translator.translate_resource(mediative_resource, standard_library.get_base_resource_standard())

    assert result_of_translation is not None
    assert type(result_of_translation) is models.Resource
    assert result_of_translation.eventAllow == True
