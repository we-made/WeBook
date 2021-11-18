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
        factory_manager.flush_state()
        calendar_buddy.register_hook(simple_hook, context_type=CalendarContext.FULLCALENDAR)
        assert len(factory_manager._FACTORY_HOOKS) == 1
    
    def test_get_hook_for_context_type (self):
        factory_manager.flush_state()
        calendar_buddy.register_hook(simple_hook, context_type=CalendarContext.FULLCALENDAR)
        assert len(factory_manager._get_hooks_for_context_type(CalendarContext.FULLCALENDAR)) == 1

    