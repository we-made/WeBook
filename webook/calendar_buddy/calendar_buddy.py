from . import base
from . import factory_manager
from typing import Callable, Optional


def register_hook(hook: Callable, context_type: base.CalendarContext) -> None:
    """ 
        Register a hook that allows you to mutate the context upon its creation, specified by context_type. 

        :param hook: The hook that is to be registered, and run on the context after fabrication
        :type hook: Callable / Function

        :param context_type: The context type that this hook applies to
        :type context_type: CalendarContext
    """
    factory_manager.register_fabrication_hook(hook=hook, context_type=context_type)


def register_defaults_for_events(defaults: dict, context_type: base.CalendarContext) -> None:
    """
        Register a set of defaults that is to be applied to all events in calendars of context_type.

        :param defaults: Dict containing the defaults to apply to all the events
        :type defaults: dict
        
        :param context_type: The context type that these defaults affect
        :type context_type: CalendarContext         
    """
    factory_manager.register_defaults(defaults=defaults,
                                      context_type=context_type,
                                      standard_type=factory_manager.StandardType.EVENT)


def register_defaults_for_resources(defaults: dict, context_type: base.CalendarContext) -> None:
    """
        Register a set of defaults that is to be applied to all resources in calendars of context_type.

        :param defaults: Dict containing the defaults to apply to all the resources
        :type defaults: dict

        :param context_type: The context type that these defaults affect
        :type context_type: CalendarContext  
    """
    factory_manager.register_defaults(defaults=defaults,
                                      context_type=context_type,
                                      standard_type=factory_manager.StandardType.RESOURCE)


def new_calendar(context_type: base.CalendarContext, events: list = [], resources: list = [], html_element_id: Optional[str] = None) -> object:
    """
        Create a new calendar instance, with the given events and resources, with the context_type deciding
        the calendar type/context.

        :param events: Start, stop and such some. Must satisfy the mediative standards.
        :type events: list of events derivated from MediativeEvent

        :param resources: For instance a room or a person. Must satisfy mediative standards.
        :type resources: list of resources derivated from MediativeResource

        :param context_type: The type of context that we want to fabricate a new calendar of. For instance FullCalendar.
        :type context_type: CalendarContext

        :return: A context, determined by context_type, that you can manipulate further before using the appropriate filter 
                 in your template, rendering the context/calendar.
        :rtype: object 
    """
    context = factory_manager.fabricate_calendar_context(context_type)
    calendar = base.Calendar(events, resources, context, html_element_id)
    context.calendar = calendar
    context.translate()
    return context
