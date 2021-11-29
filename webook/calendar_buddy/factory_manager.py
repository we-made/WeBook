from .base import CalendarContext
from typing import Callable
from enum import Enum
from .exceptions import FactoryNotFoundException
from . import base

from .contexts.fullcalendar.factory import FullCalendarFactory

# Available context factories
_CONTEXT_FACTORIES = {}
# Hooks to be run after factory identified by context type has fabcricated a context
_FACTORY_HOOKS = list()


class StandardType(Enum):
    UNDEFINED = 0
    UI_CONFIG = 1
    EVENT = 2
    RESOURCE = 3


def _get_context_factory_for_context_type(context_type: CalendarContext) -> object:
    """ 
        Get the context factory associated with the given context type 

        :param context_type: The context type of which to get the associated factory from
        :type context_type: ContextType:

        :return: Returns a factory, of which the concrete type may vary based on the context, and its implementation. In general refer to BaseCalendarContextFactory.
        :rtype: A derivation of BaseCalendarContextFactory, dependent on the type
    """
    if (context_type.value in _CONTEXT_FACTORIES):
        return _CONTEXT_FACTORIES[context_type.value]


def _get_hooks_for_context_type(context_type: CalendarContext) -> list():
    """ 
        Get the fabrication hooks associated with the given context type, these will be run after fabrication
        in the order as retrieved 

        :param context_type: The context type of which to get hooks for
        :type context_type: ContextType

        :return: Returns a list of callable hooks. Will be empty if no hooks are registered.
        :rtype: list of functions
     """
    hooks = []
    for hook in _FACTORY_HOOKS:
        if (hook["context_type"] == context_type):
            hooks.append(hook["hook"])
    return hooks


def register_context_factory(factory: base.BaseCalendarContextFactory, context_type: CalendarContext) -> None:
    """ 
        Register a new context factory, under a given context_type. There can only be one factory per context type. 

        Parameters:
            factory
                The factory to register
            
            context_type
                Which context type to register the factory to.
    """

    _CONTEXT_FACTORIES[context_type.value] = factory


def fabricate_calendar_context(context_type: CalendarContext) -> object:
    """ 
        Fabricate a new calendar context for the specified context_type
        Returns a calendar context of the type specified. E.g FullCalendarContext, if context_type is FULLCALENDAR.
        All contexts follow base.BaseCalendarContext

        Parameters:
            context_type
                Which context_type to fabricate a context for
    """

    context_factory = _get_context_factory_for_context_type(context_type)

    if context_factory is None:
        raise FactoryNotFoundException(context_type=context_type)

    constructed_context = context_factory.fabricate()

    for hook in _get_hooks_for_context_type(context_type):
        constructed_context = hook(constructed_context)

    return constructed_context


def register_fabrication_hook(hook: Callable, context_type: CalendarContext) -> None:
    """ 
        Register a fabrication hook, to be run after creating a new calendar context, on the fabricated context.
        This allows you to append your own changes to the fabrication process of this context, in a global fashion.

        Parameters:
            hook (function):
                The function that is to be registered, and later run on fabrications
                Will always receive the context, and should always return the context.

            context_type (CalendarContext):
                Designates which context this fabrication hook applies to. The factory serving
                the designated context will run the hook you supplied.

        Returns: 
            Nothing    
    """
    _FACTORY_HOOKS.append({
        "hook": hook,
        "context_type": context_type
    })


def register_defaults (defaults: dict(), context_type: CalendarContext, standard_type: StandardType) -> None:
    """
        Register a new set of defaults, for a context_type with type standard_type. This in practice
        allows you to register a set of defaults "globally" on a context - meaning it will always be 
        applied.

        Parameters:
            defaults (dict):
                A dict containing the defaults to register

            context_type (CalendarContext):
                Designates which context this standard applies to. For instance FullCalendar.
            
            standard_type (StandardType):
                Designates what kind of standard this is

        Returns: 
            Nothing
    """

    factory = _get_context_factory_for_context_type(context_type)

    if factory is None:
        raise FactoryNotFoundException(context_type=context_type)

    if standard_type == StandardType.EVENT:
        factory.event_standard = defaults
    elif standard_type == StandardType.RESOURCE:
        factory.resource_standard = defaults
    elif standard_type == StandardType.UI_CONFIG:
        factory.standard_ui_config = defaults


register_context_factory(FullCalendarFactory(), context_type=base.CalendarContext.FULLCALENDAR)