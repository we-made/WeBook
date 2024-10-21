from typing import List, Optional
from datetime import date

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


class RoomPresetGetSchema(BaseSchema):
    name: str
    rooms: List[RoomGetSchema]


class RoomPresetCreateSchema(BaseSchema):
    name: str
    rooms: List[int]


room_preset_router = CrudRouter(
    model=RoomPreset,
    tags=["roomPreset"],
    create_schema=RoomPresetCreateSchema,
    get_schema=RoomPresetGetSchema,
    update_schema=RoomPresetCreateSchema,
)
