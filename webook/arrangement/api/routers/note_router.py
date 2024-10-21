from typing import List, Optional, Union
from ninja import Router, Schema

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.paginate import paginate_queryset
from webook.arrangement.api.schemas.notes import NoteCreateSchema, NoteGetSchema
from webook.arrangement.models import Note, Person
from webook.api.crud_router import CrudRouter, ListResponseSchema, QueryFilter, Views
from datetime import datetime, date
from ninja.errors import HttpError

note_router = CrudRouter(
    model=Note,
    tags=["note"],
    create_schema=NoteCreateSchema,
    get_schema=NoteGetSchema,
    update_schema=NoteCreateSchema,
    views=[Views.LIST, Views.GET],
)
