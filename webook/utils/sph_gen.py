import hashlib
from datetime import datetime, time, timedelta

from webook.arrangement.models import PlanManifest


def get_serie_positional_hash(
    serie_uuid: str, event_title: str, start: datetime, end: datetime
) -> str:
    """Generate a serie positional hash based on MD5
    This hash can be used to uniquely identify an event inside of a serie -- before that event has been created."""
    time_format = "%H%M%d%m%Y"
    return hashlib.md5(
        f"{serie_uuid}_{event_title}_{start.strftime(time_format)}_{end.strftime(time_format)}".encode()
    ).hexdigest()
