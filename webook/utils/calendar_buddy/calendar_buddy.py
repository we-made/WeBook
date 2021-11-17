from . import base
from . import factory_manager
from typing import Callable
from enum import Enum


class CalendarContext(Enum):
    """
        Enum of recognized calendar contexts
    """

    UNDEFINED = 0
    FULLCALENDAR = 1


class Calendar:
    """
        Represents a calendar, with types and resources, while being lightly divorced from the context.
    """

    def __init__(self, events: list(), resources: list(), calendar_context: CalendarContext) -> None:
        self.events = events
        self.resources = resources
        self.context = calendar_context


class BaseCalendarContext:
    """
        The base class for calendar contexts, enforcing some hard necessities, and offering a gathering place for utilities.
    """

    def __init__(self, ui_config, calendar=None) -> None:
        self._CALENDAR = calendar
        self.ui_config = ui_config
        self.event_schema = None
        self.resource_schema = None

    def launch(self):
        """
            Run before handing the context over to the template. This is where the last minute preparations
            that must happen last are run (for instance JSON serialization of events/resources).
        """
        self.ui_config_as_dict = self.ui_config.__dict__.items()

    def events_as_json(self):
        """
            Get all events serialized to JSON
        """
        raise NotImplementedError

    def resources_as_json(self):
        """
            Get all resources serialized to JSON
        """
        raise NotImplementedError


class UIConfig:
    """
        Helps with registering, defaulting, and handling ui configuration values supplied ad-hoc on calendar
        instantiation.
    """

    def __init__(self, config_dict=None):
        self.overwrite(config_dict)

    def convert_to_dict(self) -> dict:
        return self.__dict__

    def overwrite(self, config_dict) -> UIConfig:
        """
            Overwrite the current UIConfig instance with another UIConfig instance

            Parameters:
                dict expected. Overwrite attributes by key and value.

            Returns:
                this instance (self)
        """
        if (config_dict != None):
            self.__dict__.update(config_dict)
        return self


class BaseCalendarContextFactory:
    """
        The base class for context factories. Provides utilities, and a standardized structure, for all context factories.
    """

    def _assign_specified_defaults(dict_to_write_with: dict(), dict_to_overwrite: dict()) -> dict:
        """
            Internal helper that assists with overwriting a dict, with another dict
        """
        return dict_to_overwrite.update(dict_to_write_with)

    def _mesh_defaults(self, base_defaults: dict(), specified_defaults: dict() = None) -> dict:
        if (specified_defaults != None):
            base_defaults = self._assign_specified_defaults(specified_defaults, base_defaults)
        return base_defaults

    def _get_standard_event_default(self, specified_defaults: dict() = None) -> dict:
        return self._mesh_defaults(self.event_standard, specified_defaults)

    def _get_standard_resource_default(self, specified_defaults: dict() = None) -> dict:
        return self._mesh_defaults(self.resource_standard, specified_defaults)

    def fabricate(self):
        """
            Fabricate a new calendar context
        """
        raise NotImplementedError

    def identify_self(self) -> CalendarContext:
        """
            Identify the current context
        """
        raise NotImplementedError


def new_calendar(context_type, events=[], resources=[]) -> object:
    """
        Create a new calendar instance, with the given events and resources, with the context_type deciding
        the calendar type/context. 

        Parameters:
            events: 
                Start, stop and such some. Must satisfy the mediative standards. Please refer to documentation.
            
            resources:
                For instance a room or a person. Must satisfy mediative standards. Please refer to documentation.

            context_type
                The type of context that we want to fabricate a new calendar of. For instance FullCalendar.

        Returns: 
            A context, determined by context_type, that you can manipulate further before using the appropriate filter 
            in your template, rendering the context/calendar.
    """
    
    context = factory_manager.fabricate_calendar_context(context_type)
    calendar = base.Calendar(events, resources, context)
    context.calendar = calendar
    context.translate()
    return context


def register_hook(hook: Callable, context_type: CalendarContext) -> None:
    """ 
        Register a hook that allows you to mutate the context upon its creation, specified by context_type. 
    """
    factory_manager.register_fabrication_hook(hook=hook, context_type=context_type)


def register_defaults_for_events(defaults: dict(), context_type: CalendarContext) -> None:
    """
        Register a set of defaults that is to be applied to all events in calendars of context_type.

        Parameters
            defaults:
                Dict containing the defaults to apply to all the events
            
            context_type:
                The context type that these defaults affect
    """
    factory_manager.register_defaults(defaults=defaults,
                                      context_type=context_type,
                                      standard_type=factory_manager.StandardType.EVENT)


def register_defaults_for_resources(defaults: dict(), context_type: CalendarContext) -> None:
    """
        Register a set of defaults that is to be applied to all resources in calendars of context_type.

        Parameters
            defaults:
                Dict containing the defaults to apply to all the resources
            
            context_type:
                The context type that these defaults affect
    """
    factory_manager.register_defaults(defaults=defaults,
                                      context_type=context_type,
                                      standard_type=factory_manager.StandardType.RESOURCE)
