from webook.calendar_buddy.contexts.fullcalendar.standard_library import resource_standard
import pytest

from webook.calendar_buddy.contexts.fullcalendar import factory

def test__repr__():
    test_factory = factory.FullCalendarFactory()
    result = test_factory.__repr__()
    assert result is not None  and type(result) is str and len(result) is not 0
    
def test_fabricate():
    test_factory = factory.FullCalendarFactory()
    fabricated_context = test_factory.fabricate()

    assert fabricated_context is not None
    assert fabricated_context.ui_config is not None
    assert resource_standard is not None
