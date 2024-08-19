from typing import List, Optional, Tuple
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from django.db.models import Q, Sum

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.api.validators import validate_tree_node_update
from webook.arrangement.models import Arrangement, Event
from webook.api.crud_router import CrudRouter
from datetime import datetime
from webook.arrangement.models import Audience
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet


class AudienceCreateSchema(BaseSchema):
    name: str
    name_en: Optional[str]
    parent_id: Optional[int] = None
    icon_class: Optional[str] = None


class AudienceGetSchema(ModelBaseSchema):
    id: Optional[int] = None
    slug: str
    modified: datetime
    created: datetime
    name: str
    name_en: str
    parent_id: Optional[int] = None
    icon_class: Optional[str] = None


class TreeNodeExtraDataSchema(BaseSchema):
    slug: str


class TreeNodeSchema(BaseSchema):
    id: int
    icon: str
    text: str
    children: Optional[List["TreeNodeSchema"]] = []
    data: TreeNodeExtraDataSchema


def validate_save(
    instance: Audience, payload: AudienceCreateSchema
) -> Tuple[Audience, AudienceCreateSchema]:
    """Validate the audience instance before it is saved by the router"""
    return validate_tree_node_update(instance=instance, payload=payload, model=Audience)


class AudienceRouter(CrudRouter):
    pass


audience_router = AudienceRouter(
    model=Audience,
    tags=["audience"],
    create_schema=AudienceCreateSchema,
    response_schema=AudienceGetSchema,
    update_schema=AudienceCreateSchema,
    get_schema=AudienceGetSchema,
    pre_create_hook=validate_save,
    pre_update_hook=validate_save,
)


@audience_router.get("/tree", response=List[TreeNodeSchema], by_alias=True)
def get_tree(request):
    """Get all audiences as tree"""
    return Audience.tree_dump(
        Audience.objects.all(),
    )
