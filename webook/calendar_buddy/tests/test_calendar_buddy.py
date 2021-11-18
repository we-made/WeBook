import pytest
from webook.calendar_buddy.base import CalendarContext
from webook.calendar_buddy import calendar_buddy
from webook.calendar_buddy.base import BaseCalendarContext, UIConfig
from webook.calendar_buddy import factory_manager


def simple_hook (ctx):
    print("Hook runs")
    return ctx

class TestCalendarBuddy:
    def test_register_hook (self):
        calendar_buddy.register_hook(simple_hook, context_type=CalendarContext.FULLCALENDAR)
        assert len(factory_manager._FACTORY_HOOKS) == 1
    
    def test_get_hook_for_context_type (self):
        calendar_buddy.register_hook(simple_hook, context_type=CalendarContext.FULLCALENDAR)
        assert len(factory_manager._get_hooks_for_context_type(CalendarContext.FULLCALENDAR)) == 1

    def test_register_defaults_for_events(self):
        defaults = dict()
        defaults["test"] = "testing"

        calendar_buddy.register_defaults_for_resources(
            defaults=defaults,
            context_type=CalendarContext.FULLCALENDAR,
            standard_type=factory_manager.StandardType.RESOURCE
        )

        pass

    def test_register_defaults_for_resources(self):
        pass

    def test_new_calendar(self):
        pass 
