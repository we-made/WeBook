from typing import Optional
from webook.api.crud_router import CrudRouter, QueryFilter
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.onlinebooking.api.county_router import CountyGetSchema
from webook.onlinebooking.api.schemas import SchoolCreateSchema, SchoolGetSchema
from webook.onlinebooking.models import School, County


class SchoolRouter(CrudRouter):
    def __init__(self, *args, **kwargs):
        self.list_filters = [
            QueryFilter(
                param="county_id",
                query_by="county__id",
                default=None,
                annotation=Optional[int],
            ),
            QueryFilter(
                param="city_segment_id",
                query_by="city_segment__id",
                default=None,
                annotation=Optional[int],
            ),
            QueryFilter(
                param="audience_id",
                query_by="audiences__id",
                default=None,
                annotation=Optional[int],
            ),
        ]

        super().__init__(*args, **kwargs)

        self.pre_update_hook = (
            handle_zeroing_of_segment_if_moving_to_county_without_city_segments
        )


def handle_zeroing_of_segment_if_moving_to_county_without_city_segments(
    instance: School, payload: SchoolCreateSchema
):
    new_county = County.objects.get(id=payload.county_id)
    if not new_county.city_segment_enabled:
        payload.city_segment_id = None

    return payload


school_router = SchoolRouter(
    model=School,
    tags=["School"],
    create_schema=SchoolCreateSchema,
    update_schema=SchoolCreateSchema,
    list_schema=SchoolGetSchema,
    get_schema=SchoolGetSchema,
)
