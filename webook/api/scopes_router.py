from http.client import HTTPException
from typing import List
from ninja import Router, Schema
from webook.api.crud_router import CrudRouter, Views
from webook.api.models import APIScope, APIScope

# from webook.users.api.group_router import GroupGetSchema
from webook.users.models import User


class APIScopeFullGetSchema(Schema):
    disabled: bool
    operation_id: str
    path: str

    # groups_allowed: List[GroupGetSchema]
    # users_directly_allowed: list


class APIScopeGetSchema(Schema):
    disabled: bool
    operation_id: str
    path: str


class APIScopesRouter(CrudRouter):
    model = APIScope


api_scopes_router = APIScopesRouter(
    model=APIScope,
    tags=["Scopes"],
    views=[Views.GET, Views.LIST],
    get_schema=APIScopeFullGetSchema,
    list_schema=APIScopeFullGetSchema,
)


@api_scopes_router.post("/add-scope-direct-on-user")
def add_scope_direct_on_user(request, user_id: int, scope_id: str):
    if not request.user.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    user = User.objects.get(id=user_id)
    scope = APIScope.objects.get(operation_id=scope_id)
    user.endpoint_scopes.add(scope)
    return {"success": True}


@api_scopes_router.delete("/remove-scope-direct-on-user")
def remove_scope_direct_on_user(request, user_id: int, scope_id: str):
    if not request.user.is_superuser:
        raise HTTPException(
            status_code=403, detail="You do not have permission to do this"
        )

    user = User.objects.get(id=user_id)
    scope = APIScope.objects.get(operation_id=scope_id)
    user.endpoint_scopes.remove(scope)
    return {"success": True}
