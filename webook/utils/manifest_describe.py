"""manifest_describe.py

Provides functionality to create a human friendly summary/description of what a plan manifest does, or how its schedule operates.

"""

import calendar
import re

from django.utils.translation import gettext_lazy as _

_arbitrators = {
    "0": _("first"),
    "1": _("second"),
    "2": _("third"),
    "3": _("fourth"),
    "4": _("last"),
}
"""dict: for parsing the arbitrator value/attribute on PlanManifest to a friendly strings"""


def _days_to_str(manifest) -> str:
    """Take the active days on a manifest and convert them to a readable summary
    
    So for example;
        monday, friday, saturday are selected
        the end result should then be: 'monday, friday and saturday'

    Args:
        manifest (PlanManifest): the PlanManifest from which to summarize days
    
    Returns:
        str: a comma separated summary of the active days on the given manifest
    """

    # regex replaces the last , with and
    return re.sub(r'(,)(?!.*\1)', ' and', ", ".join(map(lambda x: calendar.day_name[x], filter(lambda x: x == True, manifest.days))))


describe_pattern = {
    "daily__every_x_day": lambda manifest: _(f"Daily every {manifest.interval} day"),
    "daily__every_weekday": lambda manifest: _(f"Every weekday"),
    "weekly__standard": lambda manifest: _(f"Weekly every {_days_to_str(manifest)}"),
    "month__every_x_day_every_y_month": lambda manifest: _(f"The {manifest.day_of_month} every {manifest.interval} month"),
    "month__every_arbitrary_date_of_month": lambda manifest: _(f"Every {_arbitrators[manifest.arbitrator]} {calendar.day_name[manifest.day_of_week]} every {manifest.interval} month"),
    "yearly__every_x_of_month": lambda manifest: _(f"The {manifest.day_of_month} {calendar.month_name[manifest.month]} every {manifest.interval} year(s)"),
    "yearly__every_arbitrary_weekday_in_month": lambda manifest: f"The {_arbitrators[manifest.arbitrator]} {calendar.day_name[manifest.day_of_week]} in {calendar.month_name[manifest.month]} every {manifest.interval} year(s)",
}
"""dict: lambda functions for reading the plan manifests pattern strategy and summarizing it"""


describe_recurrence = {
    "StopWithin": lambda manifest: _(f"between {manifest.start_date} and {manifest.stop_within}"),
    "StopAfterXInstances": lambda manifest: _(f"after {manifest.stop_after_x_occurences} "),
    "NoStopDate": lambda manifest: _(f"for eternity (project {manifest.project_x_months_into_future} months into the future)"),
}
"""dict: lambda functions for reading the plan manifests recurrence strategy and summarizing it"""


def describe_manifest(manifest) -> str:
    """Generate friendly description of manifest schedule
    
    Args:
        manifest (PlanManifest): the PlanManifest for which to make a description
    
    Returns:
        str: a description of the schedule of the given manifest
    """
    return f"{describe_pattern[manifest.pattern_strategy](manifest)} {describe_recurrence[manifest.recurrence_strategy](manifest)}"
