"""manifest_describe.py

Provides functionality to create a human friendly summary/description of what a plan manifest does, or how its schedule operates.

"""

import calendar
import re

from django.utils.translation import gettext_lazy as _

_arbitrators = {
    "0": "første",
    "1": "andre",
    "2": "tredje",
    "3": "fjerde",
    "4": "siste",
}
"""dict: for parsing the arbitrator value/attribute on PlanManifest to a friendly strings"""

_day_translations = {
    "monday": "mandag",
    "tuesday": "tirsdag",
    "wednesday": "onsdag",
    "thursday": "torsdag",
    "friday": "fredag",
    "saturday": "lørdag",
    "sunday": "søndag",
}


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
    return re.sub(
        r"(,)(?!.*\1)",
        " og",
        ", ".join(
            map(
                lambda x: _day_translations[calendar.day_name[x].lower()],
                filter(lambda x: manifest.days[x] == True, manifest.days),
            )
        ),
    )


describe_pattern = {
    "daily__every_x_day": lambda manifest: f"Daglig hver {manifest.interval} dag",
    "daily__every_weekday": lambda manifest: f"Hver ukedag",
    "weekly__standard": lambda manifest: f"Ukentlig hver {_days_to_str(manifest)}",
    "month__every_x_day_every_y_month": lambda manifest: _(
        f"Den {manifest.day_of_month} hver {manifest.interval} måned"
    ),
    "month__every_arbitrary_date_of_month": lambda manifest: _(
        f"Hver {_arbitrators[manifest.arbitrator]} {calendar.day_name[manifest.day_of_week]} hver {manifest.interval} måned"
    ),
    "yearly__every_x_of_month": lambda manifest: _(
        f"Den {manifest.day_of_month} {calendar.month_name[manifest.month]} hvert {manifest.interval} år"
    ),
    "yearly__every_arbitrary_weekday_in_month": lambda manifest: f"Den {_arbitrators[manifest.arbitrator]} {calendar.day_name[manifest.day_of_week]} i {calendar.month_name[manifest.month]} hvert {manifest.interval} år",
}
"""dict: lambda functions for reading the plan manifests pattern strategy and summarizing it"""


describe_recurrence = {
    "StopWithin": lambda manifest: _(
        f"mellom {manifest.start_date.strftime('%d.%m.%Y')} og {manifest.stop_within.strftime('%d.%m.%Y')}"
    ),
    "StopAfterXInstances": lambda manifest: _(
        f"etter {manifest.stop_after_x_occurences} "
    ),
    "NoStopDate": lambda manifest: _(
        f"for evig (projiser {manifest.project_x_months_into_future} måneder inn i fremtiden)"
    ),
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
