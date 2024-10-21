from datetime import datetime

from webook.utils.utc_to_current import utc_to_current


def get_friendly_display_of_time_range(dt_a: datetime, dt_b: datetime) -> str:
    """Get friendly display text for showing a start and stop datetime"""
    
    dt_a = utc_to_current(dt_a)
    dt_b = utc_to_current(dt_b)

    date_format = "%Y.%m.%d"
    time_format = "%H:%M"
    datetime_format = date_format + " " + time_format

    is_same_day = dt_a.date() == dt_b.date()

    if is_same_day:
        return dt_a.strftime(datetime_format) + " - " + dt_b.strftime(time_format)
    else:
        return dt_a.strftime(datetime_format) + " - " + dt_b.strftime(datetime_format)


def dt_as_sortable_str(datetime: datetime) -> str:
    return datetime.strftime("%Y%m%d&H%M")
