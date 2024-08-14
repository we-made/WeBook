from webook.api.crud_router import CrudRouter
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.onlinebooking.api.schemas import CountyCreateSchema, CountyGetSchema
from webook.onlinebooking.models import County


class CountyRouter(CrudRouter):
    pass


county_router = CountyRouter(
    model=County,
    tags=["County"],
    create_schema=CountyCreateSchema,
    update_schema=CountyCreateSchema,
    list_schema=CountyGetSchema,
    get_schema=CountyGetSchema,
)
