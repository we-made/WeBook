from datetime import datetime, timezone

import pytz
from django.utils import timezone as dj_timezone


def utc_to_current(utc_dt: datetime):
    tznam = utc_dt.tzname()
    if utc_dt.tzname() != "UTC":
        return utc_dt
    current_tz = pytz.timezone(dj_timezone.get_current_timezone().zone)
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=current_tz)
