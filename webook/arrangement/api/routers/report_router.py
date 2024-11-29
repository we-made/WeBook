from typing import List, Optional
from datetime import date

from ninja import Router

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.api.mixin_routers.files_mixin_router import FileMixinRouter
from webook.arrangement.api.mixin_routers.notes_mixin_router import NotesMixinRouter
from webook.arrangement.api.mixin_routers.planner_mixin_router import PlannerMixinRouter
from webook.arrangement.api.routers.audience_router import AudienceGetSchema
from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.arrangement.api.routers.room_router import RoomGetSchema
from webook.arrangement.models import Arrangement, ArrangementFile, Person, RoomPreset
from webook.api.crud_router import CrudRouter
from datetime import datetime
import pandas as pd
from webook.arrangement.models import Event, Audience
from ninja.errors import HttpError
from ninja import File
from io import BytesIO
from django.http import HttpResponse


class RoomPresetGetSchema(BaseSchema):
    name: str
    rooms: List[RoomGetSchema]


class RoomPresetCreateSchema(BaseSchema):
    name: str
    rooms: List[int]


report_router = Router(tags=["Report"])


class ActivitesExcelReportQuerySchema(BaseSchema):
    start_date: date
    end_date: date
    main_audience: Optional[int]


@report_router.post("/activities_excel_report")
def get_activities_excel_report(
    request, query: ActivitesExcelReportQuerySchema
) -> File:
    main_audience = Audience.objects.get(id=query.main_audience)

    if not main_audience:
        raise HttpError(status=404, content={"message": "Audience not found"})

    sub_audiences = main_audience.nested_children.all()

    events = Event.objects.filter(
        audience__in=[main_audience, *sub_audiences],
        start__gte=query.start_date,
        end__lte=query.end_date,
    ).all()

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=activities_report.xlsx"

    df = pd.DataFrame(
        [
            {
                "Dato": event.start.strftime("%d.%m.%Y"),
                "Tittel": event.title,
                "Hovedmålgruppe": (
                    event.audience.parent.name
                    if event.audience.parent
                    else event.audience.name
                ),
                "Undermålgruppe": (
                    event.audience.name if event.audience.parent else None
                ),
                "Antall forventet besøkende": event.expected_visitors,
                "Antall faktisk besøkende": event.actual_visitors,
                "Arrangementstype": event.arrangement_type.name,
                "Fylke": event.county.name if event.county else None,
                "Skole": event.school.name if event.school else None,
                "Bydel": event.city_segment.name if event.city_segment else None,
            }
            for event in events
        ]
    )

    df.to_excel(response, index=False)

    return response
