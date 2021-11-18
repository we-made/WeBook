from . import standard_library
from ....calendar_buddy import base
from . context import FullCalendarContext


class FullCalendarFactory(base.BaseCalendarContextFactory):
    def __init__(self, standard_ui_config: base.UIConfig = None, event_standard: dict() = None, resource_standard: dict() = None):
        super().__init__()
        self.standard_ui_config = base.UIConfig().overwrite(standard_ui_config)
        
        self.event_standard = standard_library.event_standard()
        self.resource_standard = standard_library.resource_standard()

        # use functionality from base to mesh the base/standard default (default if nothing is supplied), with the
        # eventual defaults of the user.
        self.event_standard = self._get_standard_event_default(specified_defaults = event_standard)
        self.resource_standard = self._get_standard_resource_default(specified_defaults = resource_standard)


    def fabricate(self, custom_event_standard: list() = None, custom_resource_standard: list() = None) -> FullCalendarContext:
        if (custom_event_standard is None):
            custom_event_standard = self.event_standard
        if (custom_resource_standard is None):
            custom_resource_standard = self.resource_standard

        return FullCalendarContext(
            ui_config=self.standard_ui_config,
            event_standard=custom_event_standard,
            resource_standard=custom_resource_standard,
        )

    def __repr__(self) -> str:
        return f"<CalendarContextFactory for='FullCalendar'>"
