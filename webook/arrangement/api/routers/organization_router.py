from typing import Optional
from webook.arrangement.api.routers.organization_type_router import (
    GetOrganizationTypeSchema,
)
from webook.arrangement.models import Organization
from webook.api.crud_router import CrudRouter

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema


class CreateOrganizationSchema(BaseSchema):
    organization_number: Optional[int]
    name: str
    organization_type_id: Optional[int]
    is_archived: bool


class GetOrganizationSchema(ModelBaseSchema):
    name: str
    organization_number: Optional[int]
    organization_type: Optional[GetOrganizationTypeSchema]


organization_router = CrudRouter(
    model=Organization,
    tags=["organization"],
    create_schema=CreateOrganizationSchema,
    get_schema=GetOrganizationSchema,
    update_schema=CreateOrganizationSchema,
)
