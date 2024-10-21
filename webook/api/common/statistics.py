from typing import List, Union
from webook.api.schemas.type_statistic_schemas import (
    StatisticSchema,
    TypeMonthStatisticSchema,
    YearStatisticSchema,
)
from webook.arrangement.models import ArrangementType, Audience, Event
from django.db.models.query import QuerySet
from django.db.models import Sum
from datetime import datetime


def get_statistics_for_meta_type_by_event_set(
    events: QuerySet[Event], year: int
) -> YearStatisticSchema:
    """Get statistics for a meta type"""

    months = []

    def get_statistics(events) -> StatisticSchema:
        return StatisticSchema(
            total_arrangements=events.distinct("arrangement").count(),
            total_expected_visitors=events.aggregate(Sum("expected_visitors"))[
                "expected_visitors__sum"
            ]
            or 0,
            total_actual_visitors=events.aggregate(Sum("actual_visitors"))[
                "actual_visitors__sum"
            ]
            or 0,
            total_activities=events.count(),
            total_non_repeating_activities=events.filter(serie=None).count(),
            total_series=events.distinct("serie").count(),
        )

    for month in range(0, 12):
        events_this_month = events.filter(start__month=month + 1)
        month_name = datetime(year, month + 1, 1).strftime("%B")

        months.append(
            TypeMonthStatisticSchema(
                month=month + 1,
                month_name=month_name,
                statistics=get_statistics(events_this_month),
            )
        )

    result = YearStatisticSchema(
        year=year, months=months, whole_year=get_statistics(events)
    )

    return result
