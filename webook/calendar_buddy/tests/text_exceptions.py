from webook.calendar_buddy import exceptions
from webook.calendar_buddy.base import CalendarContext

def test_factory_notfound_exception_message_behaviour():
    """ 
        Test that FactoryNotFound exception adds a message if none is defined, 
        and does not overwrite custom message
    """
    
    exception_with_custom_message = exceptions.FactoryNotFoundException(
        context_type=CalendarContext.FULLCALENDAR,
        message="Custom Message",
        )
    
    exception_with_no_specified_message = exceptions.FactoryNotFoundException(
        context_type=CalendarContext.FULLCALENDAR,
    )

    assert exception_with_custom_message.message is not None
    assert exception_with_custom_message.message == "Custom Message"

    assert exception_with_no_specified_message.message is not None
    assert len(exception_with_no_specified_message.message) > 0