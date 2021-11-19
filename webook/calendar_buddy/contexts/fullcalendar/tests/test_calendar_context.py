import pytest
from webook.calendar_buddy.base import UIConfig, Calendar, CalendarContext
from webook.calendar_buddy.contexts.fullcalendar import context, standard_library
from webook.calendar_buddy.mediative import mediative_event, mediative_resource
from datetime import datetime


def get_test_calendar():
    calendar = Calendar(
        events=get_sample_events(),
        resources=get_sample_resources(),
        calendar_context=CalendarContext.FULLCALENDAR
    )
    return calendar

def get_sample_events():
    events = []
    events.append(
        mediative_event.MediativeEvent(
            id="1",
            title="my_title",
            start=datetime.now(),
            end=datetime.now(),
        ),
    )
    return events


def get_sample_resources():
    resources = []
    resources.append(
        mediative_resource.MediativeResource(
            id="1",
            title="my_title"
        ),
    )
    return resources


def test_context_translate():
    ui_config = UIConfig()
    test_context = context.FullCalendarContext(ui_config, calendar=get_test_calendar())
    test_context.event_standard = standard_library.event_standard()
    test_context.resource_standard = standard_library.resource_standard()
    test_context.translate()

    assert len([f for f in test_context.calendar.events if type(f) is mediative_event.MediativeEvent]) == 0
    assert len([f for f in test_context.calendar.resources if type(f) is mediative_resource.MediativeResource]) == 0


def test_events_as_json():
    ui_config = UIConfig()
    test_context = context.FullCalendarContext(ui_config)

    test_context.calendar = get_test_calendar()
    test_context.event_standard = standard_library.event_standard()
    test_context.resource_standard = standard_library.resource_standard()
    test_context.translate()
    jsonified = test_context.events_as_json()

    assert jsonified is not None and len(jsonified) != 0


def test_resources_as_json():
    ui_config = UIConfig()
    test_context = context.FullCalendarContext(ui_config)

    test_context.calendar = get_test_calendar()
    test_context.event_standard = standard_library.event_standard()
    test_context.resource_standard = standard_library.resource_standard()
    test_context.translate()
    jsonified = test_context.resources_as_json()

    assert jsonified is not None and len(jsonified) != 0


def test_context_launch():
    config = dict()
    config["view"] = 0
    config["views"] = ["dayGridMonth", "dayGridDay"]
    ui_config = UIConfig(config_dict=config)

    test_context = context.FullCalendarContext(ui_config, calendar=get_test_calendar())
    test_context.event_standard = standard_library.event_standard()
    test_context.resource_standard = standard_library.resource_standard()
    test_context.translate()
    test_context.launch()

    assert test_context.events_json is not None and type(test_context.events_json) is str
    assert test_context.resources_json is not None and type(test_context.resources_json) is str
    assert test_context.ui_config.initialView == "dayGridMonth"