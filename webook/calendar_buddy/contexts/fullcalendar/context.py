from __future__ import annotations
from typing import Optional
from ....calendar_buddy import base
from ....calendar_buddy.contexts.fullcalendar import translator
from .marshmallow_schemas import EventSchema, ResourceSchema


class FullCalendarContext(base.BaseCalendarContext):
    def __init__(self, ui_config: base.UIConfig, calendar: Optional[base.Calendar] = None,
                 event_standard: Optional[dict] = None, resource_standard: Optional[dict] = None) -> None:
        super().__init__(ui_config, calendar)
        self.calendar = calendar
        self.event_standard = event_standard
        self.resource_standard = resource_standard
        self.events_json = ""

    def configure_ui(self, **kwargs: dict) -> FullCalendarContext:
        """
            Set UI configuration variables

            :param kwargs: Config values to write into the UI config
            :type kwargs: dict

            :return: Returns this instance
            :rtype: FullCalendarContext
        """
        self.ui_config.overwrite(kwargs)
        return self

    def events_as_json(self) -> str:
        """
            Get events as json - remember to translate() first

            :return: Returns events serialized to JSON
            :rtype: str
        """
        event_schema = EventSchema()
        return event_schema.dumps(self.calendar.events, many=True)

    def resources_as_json(self) -> str:
        """
            Get resources as json - remember to translate() first
            
            :return: Returns resources serialized to JSON
            :rtype: str
        """
        resource_schema = ResourceSchema()
        return resource_schema.dumps(self.calendar.resources, many=True)

    def launch(self) -> None:
        """
            Perform last minute preparations and conversions that can't be done until just before
            we hit the rendering stage.
        """
        super().launch()
        self.ui_config.initialView = self.ui_config.views[self.ui_config.view]
        self.events_json = self.events_as_json()
        self.resources_json = self.resources_as_json()

    def translate(self) -> None:
        """
            Convert mediative events as given to us by calendarbuddy to fullcalendar compliant events
        """
        for index, event in enumerate(self.calendar.events):
            self.calendar.events[index] = translator.translate_event(event, self.event_standard)
        for index, resource in enumerate(self.calendar.resources):
            self.calendar.resources[index] = translator.translate_resource(resource, self.resource_standard)
