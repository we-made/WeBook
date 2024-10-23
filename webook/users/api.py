from http.client import HTTPException
from typing import List, Optional
from ninja import NinjaAPI
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.crud_router import CrudRouter, Views
from django.db.models import QuerySet

from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.users.models import User


class UserGetSchema(BaseSchema):
    email: str
    timezone: str
    is_user_admin: bool
    # profile_picture: str
    person: PersonGetSchema


class UserRouter(CrudRouter):
    def __init__(self, *args, **kwargs):
        self.non_deferred_fields = ["person"]
        super().__init__(*args, **kwargs)

    def get_queryset(self, view: Views = Views.GET) -> QuerySet:
        qs = super().get_queryset(view)
        qs = qs.select_related("person")
        return qs


router = UserRouter(
    model=User,
    tags=["User"],
    views=[Views.GET, Views.LIST],
    get_schema=UserGetSchema,
    list_schema=UserGetSchema,
)


@router.get("/me/", response=UserGetSchema)
def me(request):
    if request.user:
        return request.user
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")