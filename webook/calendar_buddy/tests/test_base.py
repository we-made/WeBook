import pytest
from webook.calendar_buddy.base import BaseCalendarContext, UIConfig
from webook.calendar_buddy.mediative.mediative_event import MediativeEvent
from webook.calendar_buddy.base import BaseCalendarContextFactory, Calendar, CalendarContext, UIConfig
from datetime import datetime


def factorize_context_factory ():
    return BaseCalendarContextFactory()

class TestBaseCalendarContextFactory: 
    def test_mesh_defaults (self):
        context_factory = factorize_context_factory()

        original_dict = dict()
        original_dict["test1"] = "Test100"

        new_default = dict()
        new_default["test1"] = "Test101"
        new_default["test2"] = "Test200"

        original_dict = context_factory._mesh_defaults(
            base_defaults=original_dict,
            specified_defaults=new_default,
        )

        assert len(original_dict) == 2 and original_dict["test1"] == "Test101" and "test2" in original_dict and original_dict["test2"] == "Test200"
    
    def test_mesh_defaults_on_specified_none(self):
        """ Test that None handling behaviour on standard/defaults meshing works properly """
        context_factory = factorize_context_factory()

        base_defaults = dict()
        base_defaults["Test"] = "100"
        specified_defaults = None

        meshed_dicts = context_factory._mesh_defaults(base_defaults, specified_defaults)
        assert meshed_dicts.__hash__ == base_defaults.__hash__

    def test_get_standard_event_default(self):
        context_factory = factorize_context_factory()

        specified_defaults = dict()
        specified_defaults["test"] = "test"

        standard_event_default = context_factory._get_standard_event_default(specified_defaults)

        assert standard_event_default is not None and type(standard_event_default) is dict and len(standard_event_default) == 1

    def test_get_standard_resource_default(self):
        context_factory = factorize_context_factory()

        specified_defaults = dict()
        specified_defaults["test"] = "test"

        standard_resource_default = context_factory._get_standard_resource_default(specified_defaults)

        assert standard_resource_default is not None and type(standard_resource_default) is dict and len(standard_resource_default) == 1
        
    def test_fabricate_notimplemented_error(self):
        context_factory = factorize_context_factory()

        try:
            context_factory.fabricate()
        except NotImplementedError:
            assert True

    def test_identify_self_notimplemented_error(self):
        context_factory = factorize_context_factory()

        try:
            context_factory.identify_self()
        except NotImplementedError:
            assert True


class TestCalendar:
    def test_parse_events(self):
        calendar = Calendar(events=list(), resources=list(), calendar_context = CalendarContext.FULLCALENDAR)

        events = list()

        events.append(MediativeEvent(
            id="id",
            title="test",
            start=datetime.now(),
            end=datetime.now(),
        ))

        dict_event = dict()
        dict_event["id"] = "id2"
        dict_event["title"] = "test2"
        dict_event["start"] = datetime.now()
        dict_event["end"] = datetime.now()
        dict_event["my_special_attribute"] = "very special"

        events.append(dict_event)

        calendar.events = events
        calendar._parse_events()

        assert len(calendar.events) == 2 
        assert calendar.events[1].my_special_attribute == "very special"
        assert len([ev for ev in calendar.events if type(ev) == dict]) == 0
        assert len([ev for ev in calendar.events if type(ev) == MediativeEvent]) == 2

    def test_parse_on_init(self):    
        dict_event = dict()
        dict_event["id"] = "id"
        dict_event["title"] = "test2"
        dict_event["start"] = datetime.now()
        dict_event["end"] = datetime.now()
        dict_event["my_special_attribute"] = "very special"

        events = list()
        events.append(dict_event)

        calendar = Calendar(events=events, resources=list(), calendar_context=CalendarContext.FULLCALENDAR)

        assert False

    def test_calendar_init (self):
        calendar = Calendar(events=list(), resources=list(), calendar_context = CalendarContext.FULLCALENDAR)
        assert type(calendar.events) is list
        assert type(calendar.resources) is list
        assert type(calendar.context) is CalendarContext


def factorize_calendar_context():
    pass 

class TestCalendarContext:
    def test_launch_init(self):
        ui_config = UIConfig()
        calendar_context = BaseCalendarContext(ui_config)
        assert type(calendar_context.ui_config) is UIConfig
        assert calendar_context.event_schema is None
        assert calendar_context.resource_schema is None
        assert calendar_context._CALENDAR is None
    
    def test_events_as_json_notimplemented(self):
        with pytest.raises(NotImplementedError) as e_info:
            calendar_context = BaseCalendarContext(UIConfig())
            calendar_context.events_as_json()

    def test_resources_as_json_notimplemented(self):
        with pytest.raises(NotImplementedError) as e_info:
            calendar_context = BaseCalendarContext(UIConfig())
            calendar_context.resources_as_json()


def factorize_ui_config():
    pass