from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.models import Organization, OrganizationType
from webook.api.crud_router import CrudRouter


class GetOrganizationTypeSchema(ModelBaseSchema):
    name: str


class CreateOrganizationSchema(BaseSchema):
    name: str


organization_type_router = CrudRouter(
    model=OrganizationType,
    tags=["organizationType"],
    create_schema=CreateOrganizationSchema,
    get_schema=GetOrganizationTypeSchema,
    update_schema=CreateOrganizationSchema,
)
