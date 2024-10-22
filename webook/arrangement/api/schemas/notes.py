from typing import Optional
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.api.routers.person_router import PersonGetSchema
from datetime import datetime


class NoteGetSchema(ModelBaseSchema):
    id: Optional[int] = None
    title: Optional[str] = None
    content: str
    author: PersonGetSchema
    has_personal_information: bool
    created: datetime
    modified: datetime

    arrangement_id: Optional[int] = None
    event_id: Optional[int] = None
    event_series_id: Optional[int] = None


class NoteCreateSchema(BaseSchema):
    title: str
    content: str
    has_personal_information: bool

    arrangement_id: Optional[int] = None
    event_id: Optional[int] = None
    event_series_id: Optional[int] = None
