import pytest

from webook.calendar_buddy.contexts.fullcalendar import factory

def test__repr__():
    test_factory = factory.FullCalendarFactory()
    result = test_factory.__repr__()
    assert result is not None  and type(result) is str and len(result) is not 0
    