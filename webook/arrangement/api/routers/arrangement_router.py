from typing import Any, List, Optional
from django.http import Http404
from ninja import Router, Schema
from datetime import date

from webook.api.base_list import ListApiMethod
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.m2m_rel_router_mixin import ManyToManyRelRouterMixin, RelModelDefinition
from webook.arrangement.api.mixin_routers.display_layout_mixin_router import (
    DisplayLayoutMixinRouter,
)
from webook.arrangement.api.mixin_routers.files_mixin_router import FileMixinRouter
from webook.arrangement.api.mixin_routers.notes_mixin_router import (
    NoteCreateSchema,
    NoteGetSchema,
    NotesMixinRouter,
)
from webook.arrangement.api.mixin_routers.planner_mixin_router import PlannerMixinRouter
from webook.arrangement.api.routers.arrangement_type_router import (
    ArrangementTypeGetSchema,
)
from webook.arrangement.api.routers.audience_router import AudienceGetSchema
from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.arrangement.api.routers.status_type_router import StatusTypeGetSchema
from webook.arrangement.models import Arrangement, ArrangementFile, Note, Person
from webook.api.crud_router import CrudRouter
from datetime import datetime

from webook.screenshow.api import DisplayLayoutGetSchema


class ArrangementCreateSchema(BaseSchema):
    name: str
    name_en: Optional[str] = None
    location_id: int

    meeting_place: Optional[str]
    meeting_place_en: Optional[str]

    audience_id: int
    arrangement_type_id: Optional[int]

    starts: date
    ends: date

    responsible_id: Optional[int]

    display_text: Optional[str]
    display_text_en: Optional[str]

    display_layouts: Optional[List[DisplayLayoutGetSchema]] = []


class ArrangementGetSchema(ModelBaseSchema):
    id: Optional[int] = None
    slug: str
    name: str
    name_en: Optional[str] = None
    location_id: int
    meeting_place: Optional[str]
    meeting_place_en: Optional[str]

    audience_id: int
    audience: Optional[AudienceGetSchema]

    arrangement_type_id: Optional[int]
    arrangement_type: Optional[ArrangementTypeGetSchema]

    status_id: Optional[int]
    status: Optional[StatusTypeGetSchema]

    starts: Optional[datetime]
    ends: Optional[datetime]
    responsible_id: Optional[int]
    responsible: Optional[PersonGetSchema]

    display_text: Optional[str]
    display_text_en: Optional[str]

    show_on_multimedia_screen: bool = False

    planners: Optional[List[PersonGetSchema]]


class ArrangementRouter(
    CrudRouter,
    NotesMixinRouter,
    FileMixinRouter,
    PlannerMixinRouter,
    DisplayLayoutMixinRouter,
):
    # m2m_rel_fields = {
    #     "notes": RelModelDefinition(
    #         field_name="notes",
    #         relation_model_type=Note,
    #         get_schema=NoteGetSchema,
    #         create_schema=NoteCreateSchema,
    #     ),
    # }

    # always_included_rel_fields = [
    #     "location",
    #     "responsible",
    #     "status",
    #     "audience",
    #     "arrangement_type",
    # ]

    non_deferred_fields = [
        "display_layouts",
        "people_participants",
        "planners",
        "notes",
        "responsible",
        "status",
        "audience",
        "arrangement_type",
        "location",
    ]

    file_model = ArrangementFile


arrangement_router = ArrangementRouter(
    model=Arrangement,
    tags=["arrangement"],
    get_schema=ArrangementGetSchema,
    create_schema=ArrangementCreateSchema,
    response_schema=ArrangementGetSchema,
    update_schema=ArrangementCreateSchema,
)


class GetStructuredListOfRepeatingAndEvents(ListApiMethod):
    def marshall_data(
        self,
        arrangement_id: int,
        page: int = 1,
        limit: int = 100,
        search: str = None,
        include_archived: bool = False,
        fields_to_search: str = None,
        sort_by: str = None,
        sort_desc: bool = False,
        **extra_params: Any
    ) -> Any:
        arrangement = Arrangement.objects.get(pk=arrangement_id)

        if arrangement is None:
            raise Http404("Arrangement not found")

        series = arrangement.series.all()

        # We want a list of series and events.
        # Events will be events without a serie.

        events = arrangement.events.filter(serie=None)

    def __call__(
        self,
        arrangement_id: int,
        page: int = 1,
        limit: int = 100,
        search: str = None,
        include_archived: bool = False,
        fields_to_search: str = None,
        sort_by: str = None,
        sort_desc: bool = False,
        **extra_params: Any
    ) -> Any:
        return self.marshall_data(
            arrangement_id=arrangement_id,
            page=page,
            limit=limit,
            search=search,
            include_archived=include_archived,
            fields_to_search=fields_to_search,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
