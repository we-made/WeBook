from typing import List, Optional
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import Router, Schema

from django.db.models import Q

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.common.statistics import get_statistics_for_meta_type_by_event_set
from webook.api.crud_router import CrudRouter
from webook.api.schemas.type_statistic_schemas import (
    MetaTypeDistributionSchema,
    MetaTypeStatisticSummarySchema,
    YearStatisticSchema,
)
from webook.arrangement.models import Arrangement, Audience, Event
from datetime import datetime
from webook.arrangement.models import StatusType
from webook.api.types.color import Color


class StatusTypeCreateSchema(BaseSchema):
    name: str
    color: Color


class StatusTypeGetSchema(ModelBaseSchema):
    id: Optional[int] = None
    slug: str
    modified: datetime
    created: datetime
    color: Color
    name: str


status_type_router = CrudRouter(
    tags=["statusType"],
    model=StatusType,
    create_schema=StatusTypeCreateSchema,
    update_schema=StatusTypeCreateSchema,
    get_schema=StatusTypeGetSchema,
)


@status_type_router.get(
    "/statistics/{id}/{year}", response=YearStatisticSchema, by_alias=True
)
def get_statistics(request, id: int, year: int):
    """Get statistics for a given year"""
    audience = get_object_or_404(StatusType, pk=id)

    events = Event.objects.filter(Q(status=audience) & Q(start__year=year)).all()

    return get_statistics_for_meta_type_by_event_set(events, year)


@status_type_router.get(
    "/statisticSummary/{year}", response=MetaTypeStatisticSummarySchema, by_alias=True
)
def get_summary_statistic(request, year: int):
    status_types = StatusType.objects.all()

    summary = MetaTypeStatisticSummarySchema(
        total_arrangements=0,
        total_activities=0,
        arrangement_distribution=[],
        activity_distribution=[],
    )

    for status in status_types:
        summary.total_arrangements += Event.objects.filter(
            Q(status=status) & Q(start__year=year)
        ).count()

        summary.total_activities += Event.objects.filter(
            Q(status=status) & Q(start__year=year)
        ).count()

        summary.arrangement_distribution.append(
            MetaTypeDistributionSchema(
                name=status.name,
                count=status.status_of_arrangements.all().count(),
            )
        )

        summary.activity_distribution.append(
            MetaTypeDistributionSchema(
                name=status.name,
                count=Event.objects.filter(
                    Q(status=status) & Q(start__year=year)
                ).count(),
            )
        )

    return summary
