import pytest
from webook.calendar_buddy.base import CalendarContext
from webook.calendar_buddy import calendar_buddy
from webook.calendar_buddy.base import BaseCalendarContext, UIConfig
from webook.calendar_buddy import factory_manager
from webook.calendar_buddy.tests import test_factory_manager

def simple_hook (ctx):
    print("Hook runs")
    return ctx

class TestCalendarBuddy:
    def test_register_hook (self):
        factory_manager.flush_state()
        calendar_buddy.register_hook(simple_hook, context_type=CalendarContext.FULLCALENDAR)
        assert len(factory_manager._FACTORY_HOOKS) == 1
    
    def test_get_hook_for_context_type (self):
        factory_manager.flush_state()
        calendar_buddy.register_hook(simple_hook, context_type=CalendarContext.FULLCALENDAR)
        assert len(factory_manager._get_hooks_for_context_type(CalendarContext.FULLCALENDAR)) == 1

    def test_register_defaults_for_event(self):
        factory_manager.flush_state()
        test_factory_manager.register_testing_calendarcontext_factory()
        defaults = dict()
        defaults["something"] = "something something"
        calendar_buddy.register_defaults_for_events(
            defaults=defaults,
            context_type=CalendarContext.FULLCALENDAR
        )
        ctx_factory = factory_manager._CONTEXT_FACTORIES[1]
        assert ctx_factory is not None and ctx_factory.event_standard is not None
        assert "something" in ctx_factory.event_standard

    def test_register_defaults_for_resource(self):
        factory_manager.flush_state()
        test_factory_manager.register_testing_calendarcontext_factory()
        defaults = dict()
        defaults["something"] = "something something"
        calendar_buddy.register_defaults_for_resources(
            defaults=defaults,
            context_type=CalendarContext.FULLCALENDAR
        )
        ctx_factory = factory_manager._CONTEXT_FACTORIES[1]
        assert ctx_factory is not None and ctx_factory.event_standard is not None
        assert "something" in ctx_factory.resource_standard
    