from datetime import datetime, timezone
from django.utils import timezone as dj_timezone

import pytz

def utc_to_current(utc_dt):
    current_tz = pytz.timezone(dj_timezone.get_current_timezone().key)
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=current_tz)