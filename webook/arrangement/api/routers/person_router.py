from typing import List, Optional, Union
from ninja import Router, Schema
from pydantic import Extra

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.paginate import paginate_queryset
from webook.arrangement.models import Person
from webook.api.crud_router import CrudRouter, ListResponseSchema, QueryFilter
from datetime import datetime, date
from ninja.errors import HttpError


class PersonCreateSchema(BaseSchema):
    social_provider_id: Optional[str]
    social_provider_email: Optional[str]
    personal_email: str
    first_name: str
    middle_name: str = ""
    last_name: str
    birth_date: Optional[date]


class PersonGetSchema(ModelBaseSchema, extra="allow"):
    id: Optional[int] = None
    social_provider_id: Optional[str]
    social_provider_email: Optional[str]
    personal_email: str
    first_name: str
    middle_name: str
    last_name: str
    birth_date: Optional[date]
    modified: datetime
    created: datetime

    is_sso_capable: bool
    is_synced: bool
    full_name: str


class PersonFilterSchema(Schema):
    groups: Optional[List[str]]


class PersonRouter(CrudRouter):

    def __init__(self, *args, **kwargs):
        self.list_filters = [
            QueryFilter(
                param="group",
                query_by="user__groups__name",
                default=None,
                annotation=Optional[str],
            ),
            QueryFilter(
                param="sysadminsOnly",
                query_by="user__is_superuser",
                default=None,
                annotation=Optional[bool],
            ),
        ]

        super().__init__(*args, **kwargs)


person_router = PersonRouter(
    model=Person,
    tags=["person"],
    create_schema=PersonCreateSchema,
    get_schema=PersonGetSchema,
    update_schema=PersonCreateSchema,
    enable_search=True,
)
