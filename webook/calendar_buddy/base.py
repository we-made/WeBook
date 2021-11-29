from __future__ import annotations
from enum import Enum
from .mediative import mediative_event


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
        self._parse_events()

    def _parse_events (self):
        """ 
            Parse the events. If they are stored as dicts, convert them into MediativeEvent if possible.
        """
        converted_events = list()
        for event in self.events:
            if (type(event) == dict):
                converted_event = mediative_event.MediativeEvent(id = event["id"], title = event["title"], start = event["start"], end = event["end"])
                keys_not_in = [y for y in event if y not in dir(converted_event)]
                for f in keys_not_in:
                    converted_event.__dict__[f] = event[f]
                converted_events.append(converted_event)
            else: 
                converted_events.append(event)

        self.events = converted_events



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

            :raises NotImplementedError: Raises not implemented error if not implemented by the derivative
        """
        raise NotImplementedError

    def resources_as_json(self):
        """
            Get all resources serialized to JSON

            :raises NotImplementedError: Raises not implemented error if not implemented by the derivative
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
        """
            Returns a converted version of the current UIConfig instance as a dict

            :return: A dict equivalent of the current instance
            :rtype: dict
        """
        return self.__dict__

    def overwrite(self, config_dict) -> UIConfig:
        """
            Overwrite the current UIConfig instance with a dict

            :param config_dict: The dict which is to overwrite the existing UIConfig values
            :type config_dict: dict

            :return: Returns this instance/this UIConfig
            :rtype: UIConfig
        """
        if (config_dict != None):
            self.__dict__.update(config_dict)
        return self


class BaseCalendarContextFactory:
    """
        The base class for context factories. Provides utilities, and a standardized structure, for all context factories.
    """

    def __init__(self) -> None:
        self.event_standard = dict()
        self.resource_standard = dict()

    def _mesh_defaults(self, base_defaults: dict(), specified_defaults: dict() = None) -> dict:
        if (specified_defaults != None):
            base_defaults.update(specified_defaults)
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