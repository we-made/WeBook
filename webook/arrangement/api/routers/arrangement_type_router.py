from typing import List, Optional, Tuple
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from ninja import Router, Schema

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.common.statistics import get_statistics_for_meta_type_by_event_set
from webook.api.schemas.type_statistic_schemas import (
    MetaTypeDistributionSchema,
    MetaTypeStatisticSummarySchema,
    YearStatisticSchema,
)
from webook.api.shared_validators import validate_tree_node_update
from webook.arrangement.api.routers.audience_router import TreeNodeSchema
from webook.arrangement.models import Arrangement, ArrangementType, Audience, Event
from webook.api.crud_router import CrudRouter
from datetime import datetime
from django.db.models import Q


class ArrangementTypeCreateSchema(BaseSchema):
    name: str
    name_en: str
    parent_id: Optional[int] = None


class ArrangementTypeGetSchema(ModelBaseSchema):
    id: Optional[int] = None
    name: str
    name_en: str
    parent_id: Optional[int] = None
    is_archived: bool
    modified: datetime
    created: datetime


def validate_save(
    instance: ArrangementType, payload: ArrangementTypeCreateSchema
) -> Tuple[ArrangementType, ArrangementTypeCreateSchema]:
    """Validate the arrangement type instance before it is saved by the router"""
    return validate_tree_node_update(
        instance=instance, payload=payload, model=ArrangementType
    )


class ArrangementTypeRouter(CrudRouter):
    def transform_to_export(
        self, instances: List[ArrangementType]
    ) -> HttpResponseBadRequest:
        return list(
            map(
                lambda instance: {
                    "Navn": instance.name,
                    "Navn (Engelsk)": instance.name_en,
                    "Forelder": instance.parent.name if instance.parent else "Ingen",
                    "Oppdatert": instance.modified,
                    "Opprettet": instance.created,
                },
                instances,
            )
        )


arrangement_type_router = ArrangementTypeRouter(
    model=ArrangementType,
    tags=["arrangementType"],
    create_schema=ArrangementTypeCreateSchema,
    get_schema=ArrangementTypeGetSchema,
    update_schema=ArrangementTypeCreateSchema,
    pre_create_hook=validate_save,
    pre_update_hook=validate_save,
    export_exclude_fields=[
        "is_archived",
        "parent_id",
        "archived_by_id",
        "archived_when",
    ],
)


@arrangement_type_router.get("/tree", response=List[TreeNodeSchema], by_alias=True)
def get_tree(request):
    return ArrangementType.tree_dump(
        ArrangementType.objects.all(),
    )


@arrangement_type_router.get(
    "/statistics/{id}/{year}", response=YearStatisticSchema, by_alias=True
)
def get_statistics(request, id: int, year: int):
    arrangement_type = get_object_or_404(ArrangementType, pk=id)

    events = Event.objects.filter(
        Q(arrangement_type=arrangement_type) & Q(start__year=year)
    ).all()

    return get_statistics_for_meta_type_by_event_set(events, year)


@arrangement_type_router.get(
    "/statisticSummary/{year}", response=MetaTypeStatisticSummarySchema, by_alias=True
)
def get_summary_statistic(request, year: int):
    arrangement_types = ArrangementType.objects.all()

    summary = MetaTypeStatisticSummarySchema(
        total_arrangements=0,
        total_activities=0,
        arrangement_distribution=[],
        activity_distribution=[],
    )

    for arrangement_type in arrangement_types:
        summary.total_arrangements += Event.objects.filter(
            Q(arrangement_type=arrangement_type) & Q(start__year=year)
        ).count()

        summary.total_activities += Event.objects.filter(
            Q(arrangement_type=arrangement_type) & Q(start__year=year)
        ).count()

        summary.arrangement_distribution.append(
            MetaTypeDistributionSchema(
                name=arrangement_type.name,
                count=arrangement_type.arrangements.all().count(),
            )
        )

        summary.activity_distribution.append(
            MetaTypeDistributionSchema(
                name=arrangement_type.name,
                count=Event.objects.filter(
                    Q(arrangement_type=arrangement_type) & Q(start__year=year)
                ).count(),
            )
        )

    return summary
