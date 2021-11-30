from . import standard_library
from ....calendar_buddy import base
from . context import FullCalendarContext
from typing import Optional


class FullCalendarFactory(base.BaseCalendarContextFactory):
    """
        A factory which can fabricate FullCalendarContexts
    """

    def __init__(self, standard_ui_config: base.UIConfig = None, event_standard: Optional[dict] = None, resource_standard: Optional[dict] = None) -> None:
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

        self.event_standard = standard_library.get_base_event_standard()
        self.resource_standard = standard_library.get_base_resource_standard()

        # use functionality from base to mesh the base/standard default (default if nothing is supplied), with the
        # eventual defaults of the user.
        self.event_standard = self._get_standard_event_default(specified_defaults=event_standard)
        self.resource_standard = self._get_standard_resource_default(specified_defaults=resource_standard)

    def fabricate(self, custom_event_standard: Optional[list] = None, custom_resource_standard: Optional[list] = None) -> FullCalendarContext:
        """
            Fabricate a new FullCalendarContext

            :param custom_event_standard: A event standard to use for just this fabrication
            :type custom_event_standard: list

            :param custom_resource_standard: A resource standard to use for just this fabrication
            :type custom_resource_standard: list

            :return: Returns a newly fabricated FullCalendarContext, composed and molded based on the standards and hooks supplied
            :rtype: FullCalendarContext
        """
        if custom_event_standard is None:
            custom_event_standard = self.event_standard
        if custom_resource_standard is None:
            custom_resource_standard = self.resource_standard

        return FullCalendarContext(
            ui_config=self.standard_ui_config,
            event_standard=custom_event_standard,
            resource_standard=custom_resource_standard,
        )

    def __repr__(self) -> str:
        return f"<CalendarContextFactory for='FullCalendar'>"
