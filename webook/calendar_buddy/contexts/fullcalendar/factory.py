from ....calendar_buddy import base
from . context import FullCalendarContext
from .models import EventDisplay

import datetime


class FullCalendarFactory(base.BaseCalendarContextFactory):
    """
        A factory which can fabricate FullCalendarContexts
    """

    def __init__(self, standard_ui_config: base.UIConfig = None, event_standard: dict() = None, resource_standard: dict() = None) -> None:
        """
            Initialize the FullCalendarFactory

            :param standard_ui_config: The standard base UI config that this factory is to adhere to when fabricating in the future. May be None.
            :type standard_ui_config: UIConfig

            :param event_standard: The standard event defaults that this factory is to adhere to when fabricating. May be None.
            :type event_standard: dict

            :param resource_standard: The standard resource defaults that this factory is to adhere to when fabricating. May be None.
            :type resource_standard: dict
        """
        super().__init__()
        self.standard_ui_config = base.UIConfig().overwrite(standard_ui_config)
        self.event_standard = self._get_standard_event_default(specified_defaults = event_standard)
        self.resource_standard = self._get_standard_resource_default(specified_defaults = resource_standard)
        
        self.event_standard = dict()
        self.event_standard["groupId"] = ""
        self.event_standard["allDay"] = False
        self.event_standard["start"] = datetime.datetime.now()
        self.event_standard["end"] = datetime.datetime.now()
        self.event_standard["startStr"] = ""
        self.event_standard["endStr"] = ""
        self.event_standard["url"] = ""
        self.event_standard["classNames"] = []
        self.event_standard["editable"] = False
        self.event_standard["startEditable"] = False
        self.event_standard["durationEditable"] = False
        self.event_standard["resourceEditable"] = False
        self.event_standard["display"] = EventDisplay.AUTO
        self.event_standard["overlap"] = None
        self.event_standard["constraint"] = None
        self.event_standard["backgroundColor"] = ""
        self.event_standard["borderColor"] = ""
        self.event_standard["textColor"] = ""
        self.event_standard["extendedProps"] = []
        self.event_standard["source"] = None

        self.resource_standard = dict()
        self.resource_standard["extendedProps"] = []
        self.resource_standard["eventConstraint"] = None
        self.resource_standard["eventOverlap"] = False
        self.resource_standard["eventAllow"] = False
        self.resource_standard["eventBackgroundColor"] = ""
        self.resource_standard["eventBorderColor"] = ""
        self.resource_standard["eventTextColor"] = ""
        self.resource_standard["eventClassNames"] = []


    def fabricate(self, custom_event_standard: list() = None, custom_resource_standard: list() = None) -> FullCalendarContext:
        """
            Fabricate a new FullCalendarContext

            :param custom_event_standard: A event standard to use for just this fabrication
            :type custom_event_standard: list

            :param custom_resource_standard: A resource standard to use for just this fabrication
            :type custom_resource_standard: list

            :return: Returns a newly fabricated FullCalendarContext, composed and molded based on the standards and hooks supplied
            :rtype: FullCalendarContext
        """
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
