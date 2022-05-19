from dataclasses import dataclass
from typing import List, Optional
from webook.arrangement.models import PlanManifest
from datetime import datetime, timedelta, time


@dataclass
class _Scope:
    start_date: datetime
    stop_within_date: datetime
    instance_limit: int


@dataclass
class _Event:
    title: str
    start: time
    end: time


@dataclass
class _CycleInstruction:
    cycle: int
    start_date: datetime
    event: _Event
    arbitrator: Optional[int]
    interval: Optional[int]
    days: Optional[dict]
    day_of_month: Optional[int]
    day_of_week: Optional[int]
    day_index: Optional[int]
    month: Optional[int]


@dataclass
class _RecurrenceInstruction:
    """ Instructions for how recurrence is to be calculated (cycling) """
    start_date: datetime
    stop_within_date: datetime
    instances: Optional[int]
    projection_distance_in_months: Optional[int]


def _overwrite_time(write_to_datetime: datetime, time_from_datetime: datetime):
    """ 
        Overwrite the time values of datetime with that of another datetime and 
        return a new datetime 
    """
    return write_to_datetime.replace(
        hour=time_from_datetime.hour,
        minute=time_from_datetime.minute,
        second=time_from_datetime.second,
    )


def _days_to_dict (serie_manifest: PlanManifest) -> dict:
    """ Takes the days on a PlanManifest and returns it in dict form """
    return {
        0: serie_manifest.monday,
        1: serie_manifest.tuesday,
        2: serie_manifest.wednesday,
        3: serie_manifest.thursday,
        4: serie_manifest.friday,
        5: serie_manifest.saturday,
        6: serie_manifest.sunday
    }


def _day_seek(start_date: datetime, arbitrator: int, weekday: int) -> datetime:
    """
        Given a start_date, arbitrator and day of week, this function will find the 
        date decided by arbitrator and weekday, in the given month of start_date.
        To give a more practical example; say you have arbitrator "second" and weekday tuesday.
        In which case you would get the datetime of the second tuesday in the month defined by start_date.
        The arbitrator is a non fixed arbitrary position. Wording may be a bit off.
    """

    # A note about the arbitrator variable:
    # 0 = first
    # 1 = second
    # 2 = third
    # 3 = fourth
    # 4 = last

    weekday = weekday
    date = start_date.replace(day=1)

    # figure out the diff between the weekday we are currently "cursored" on, and the one we want to be on
    weekday_diff = date.weekday() - weekday

    # move the date to the desired day of week - this may be out of bounds of the desired months
    date = date + timedelta(days = weekday_diff * (-1 if weekday_diff > 0 else 1))
    # are we still in the desired month? if not move a week forward to get to the first ocurrence of the desired weekday
    if date.month != start_date.month:
        date = date + timedelta(days=7)

    # at this point we have found the first ocurrence of the day of week we want
    # we can now simply * 7 to move forwards with the weeks as they go.
    date = date + timedelta(days = (arbitrator * 7))

    # Special handling for when one wants the last instance of a weekday. Not always a given that the last instance of the weekday
    # is on the last week.
    if arbitrator == 4 and date.month != start_date.month:
        date = date + timedelta(days = 4 * 7)
    
    return date


def _pattern_strategy_daily_every_x_day(cycle: _CycleInstruction) -> _Event:
    if cycle.cycle != 0:
        cycle.start_date += timedelta(days = cycle.interval - 1)
    
    cycle.event.start = _overwrite_time(write_to_datetime=cycle.start_date, time_from_datetime=cycle.event.start)
    cycle.event.end =   _overwrite_time(write_to_datetime=cycle.start_date, time_from_datetime=cycle.event.end)

    return cycle.event


def _pattern_strategy_daily_every_weekday(cycle: _CycleInstruction) -> _Event:
    while cycle.start_date.weekday in [5,6]:
        cycle.start_date += timedelta(days = 1)

    cycle.event.start = cycle.start_date.replace(
        hour=cycle.event.start.hour,
        minute=cycle.event.start.minute,
        second=cycle.event.end.second
    )

    return cycle.event


def _pattern_strategy_weekly_standard(cycle: _CycleInstruction) -> List[_Event]:
    if cycle.cycle != 0:
        if  cycle.start_date.weekday() != 0:
            cycle.start_date += timedelta(days = (cycle.start_date.weekday() - 1) * -1 )
        cycle.start_date += timedelta(7 * cycle.interval)
    
    events = []
    counter = 0
    for day in range(cycle.start_date.weekday(), 0, 6):
        if day in cycle.days and cycle.days[day] == True:
            adjusted_start_date = cycle.start_date + timedelta(days=counter)
            cycle.event.start = _overwrite_time(write_to_datetime=adjusted_start_date, time_from_datetime=cycle.event.start)
            cycle.event.end = _overwrite_time(write_to_datetime=adjusted_start_date, time_from_datetime=cycle.event.end)
            events.append(cycle.event)
        
        counter += 1
    
    return events


def _pattern_strategy_every_x_day_every_y_month(cycle: _CycleInstruction) -> _Event:
    if cycle != 0:
        cycle.start_date += timedelta( weeks = 4 * cycle.interval )
        cycle.start_date.day = 1
    
    if cycle.day_of_month > cycle.start_date.day:
        return

    adjusted_date = cycle.start_date.replace(day=cycle.day_of_month)
    cycle.event.start = _overwrite_time(write_to_datetime=adjusted_date, time_from_datetime=cycle.event.start)
    cycle.event.end = _overwrite_time(write_to_datetime=adjusted_date, time_from_datetime=cycle.event.end)

    return cycle.event


def _pattern_strategy_every_arbitrary_date_of_month(cycle: _CycleInstruction) -> _Event:
    if cycle != 0:
        cycle.start_date = cycle.start_date.replace(day=1, month=cycle.start_date.month + cycle.interval)
    
    date = _day_seek(cycle.start_date, cycle.arbitrator, cycle.day_of_week)
    cycle.event.start = _overwrite_time(write_to_datetime=date, time_from_datetime=cycle.event.start)
    cycle.event.end = _overwrite_time(write_to_datetime=date, time_from_datetime=cycle.event.end)

    return cycle.event


def _pattern_strategy_yearly_every_x_of_month(cycle: _CycleInstruction) -> _Event:
    if cycle != 0:
        cycle.start_date.replace(year = cycle.start_date.year + cycle.interval)
    
    date = cycle.start_date.replace(month=cycle.month, day=cycle.day_index)
    cycle.event.start = _overwrite_time(write_to_datetime=date, time_from_datetime=cycle.event.start)
    cycle.event.end = _overwrite_time(write_to_datetime=date, time_from_datetime=cycle.event.end)

    return cycle.event


def _pattern_strategy_arbitrary_weekday_in_month(cycle: _CycleInstruction) -> _Event:
    if cycle != 0:
        cycle.start_date.replace(year=cycle.start_date.year + cycle.interval)
    
    date = _day_seek(cycle.start_date.replace(month=cycle.month), cycle.arbitrator, cycle.day_of_week)
    _overwrite_time(write_to_datetime=date, time_from_datetime=cycle.event.start)
    _overwrite_time(write_to_datetime=date, time_from_datetime=cycle.event.end)

    return cycle.event


def _area_strategy_stopwithin(recurrence_instructions: _RecurrenceInstruction) -> _Scope:
    return _Scope(
        start_date=recurrence_instructions["start_date"],
        stop_within_date=recurrence_instructions["stop_within_date"],
        instance_limit=0
    )


def _area_strategy_stop_after_x_instances(recurrence_instructions: _RecurrenceInstruction) -> _Scope:
    return _Scope(
        start_date=recurrence_instructions["start_date"],
        stop_within_date=None,
        instance_limit=recurrence_instructions["instances"]
    )


def _area_strategy_no_stop_date(recurrence_instructions: _RecurrenceInstruction) -> _Scope:
    stop_within_date = recurrence_instructions["start_date"] + timedelta( weeks = 4 * recurrence_instructions["projection_distance_in_months"] )

    return _Scope(
        start_date=recurrence_instructions["start_date"],
        stop_within_date=stop_within_date,
        instance_limit=0
    )


_pattern_strategies = {
    "daily__every_x_day": _pattern_strategy_daily_every_x_day,
    "daily__every_weekday": _pattern_strategy_daily_every_weekday,
    "weekly__standard": _pattern_strategy_weekly_standard,
    "month__every_x_day_every_y_month": _pattern_strategy_every_x_day_every_y_month,
    "month__every_arbitrary_date_of_month": _pattern_strategy_every_arbitrary_date_of_month,
    "yearly__every_x_of_month": _pattern_strategy_yearly_every_x_of_month,
    "yearly__every_arbitrary_weekday_in_month": _pattern_strategy_arbitrary_weekday_in_month,
}

_area_strategies = {
    "StopWithin": _area_strategy_stopwithin,
    "StopAfterXInstances": _area_strategy_stop_after_x_instances,
    "NoStopDate": _area_strategy_no_stop_date,
}


def calculate_serie(serie_manifest: PlanManifest) -> List[_Event]:
    """ 
        Takes a serie manifest (PlanManifest) and calculates it, and returns the resulting events of said calculation.
    """

    recurrence_instructions = _RecurrenceInstruction(
        start_date = serie_manifest.start_date,
        stop_within_date = serie_manifest.stop_within,
        instances = serie_manifest.stop_after_x_occurences,
        projection_distance_in_months = serie_manifest.project_x_months_into_future,
    )

    area_strategy = _area_strategies[serie_manifest.recurrence_strategy]
    scope = area_strategy(recurrence_instructions)
    pattern_strategy = _pattern_strategies[serie_manifest.pattern_strategy]

    events = []

    date_cursor = scope.start_date
    instance_cursor, cycle_cursor = 0

    while ((scope.stop_within_date is not None and date_cursor < scope.stop_within_date) 
            or (scope.instance_limit != 0 and scope.instance_limit >= instance_cursor)):

            cycle_instruction = _CycleInstruction(
                cycle=cycle_cursor,
                start_date=date_cursor,
                event=_Event(title=serie_manifest.title, start=serie_manifest.start_time, end=serie_manifest.end_time),
                arbitrator=serie_manifest.arbitrator,
                interval=serie_manifest.interval,
                days=_days_to_dict(serie_manifest),
                day_of_month=serie_manifest.day_of_month,
                day_of_week=serie_manifest.day_of_week,
                day_index=serie_manifest.day_of_month, # TODO: Check the validity of this
                month=serie_manifest.month,
            )

            result = pattern_strategy( cycle_instruction )

            if result is None or ( isinstance(result, list) and len(result) == 0 ):
                cycle_cursor += 1
                continue
            
            if (scope.stop_within_date is not None and result.start >= scope.stop_within_date 
                    or scope.instance_limit is not None and instance_cursor > scope.instance_limit):
                break

            if isinstance(result, list):
                date_cursor = result[-1].end
                events += result
            else:
                date_cursor = result.end
                events.append(result)

            date_cursor += timedelta(days=1)

            if scope.instance_limit != 0:
                instance_cursor += 1
            
            cycle_cursor += 1
    
    return events