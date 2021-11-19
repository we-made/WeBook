from __future__ import annotations
from ....calendar_buddy import base
from ....calendar_buddy.contexts.fullcalendar import translator
from .marshmallow_schemas import EventSchema, ResourceSchema


class FullCalendarContext(base.BaseCalendarContext):
    def __init__(self, ui_config, calendar=None,
                 event_standard=None, resource_standard=None) -> None:
        super().__init__(ui_config, calendar)
        self.calendar = calendar
        self.event_standard = event_standard
        self.resource_standard = resource_standard
        self.events_json = ""

    def configure_ui(self, **kwargs) -> FullCalendarContext:
        """
            Set UI configuration variables

            Parameters:
                kwargs:
                    Config values to write into the UI config
        """
        self.ui_config.overwrite(kwargs)
        return self

    def events_as_json(self) -> str:
        """
            Get events as json - remember to translate() first
        """
        event_schema = EventSchema()
        return event_schema.dumps(self.calendar.events, many=True)

    def resources_as_json(self) -> str:
        """
            Get resources as json - remember to translate() first
        """
        resource_schema = ResourceSchema()
        return resource_schema.dumps(self.calendar.resources, many=True)

    def launch(self) -> None:
        super().launch()
        self.ui_config.initialView = self.ui_config.views[self.ui_config.view]
        self.events_json = self.events_as_json()
        self.resources_json = self.resources_as_json()

    def translate(self) -> None:
        """
            Convert mediative events to fullcalendar events
        """
        for index, event in enumerate(self.calendar.events):
            self.calendar.events[index] = translator.translate_event(event, self.event_standard)
        for index, resource in enumerate(self.calendar.resources):
            self.calendar.resources[index] = translator.translate_resource(resource, self.resource_standard)
