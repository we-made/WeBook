from typing import List, Optional
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import Router, Schema

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.crud_router import CrudRouter
from webook.arrangement.models import Room


class RoomCreateSchema(BaseSchema):
    name: str
    name_en: Optional[str]
    location_id: Optional[int]
    max_capacity: int
    is_exclusive: bool
    has_screen: bool
    is_archived: bool


class RoomGetSchema(ModelBaseSchema):
    id: Optional[int] = None
    name: str
    name_en: Optional[str]
    location_id: Optional[int]
    max_capacity: int
    is_exclusive: bool
    has_screen: bool


room_router = CrudRouter(
    tags=["rooms"],
    model=Room,
    create_schema=RoomCreateSchema,
    update_schema=RoomCreateSchema,
    get_schema=RoomGetSchema,
)


@room_router.get("/tree", response=List[RoomGetSchema], by_alias=True)
def get_tree(request):
    return [item.as_node() for item in Room.objects.all()]
