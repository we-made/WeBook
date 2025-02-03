from ninja.errors import HttpError
from webook.api.models import ServiceAccount
from webook.users.models import User
from typing import Union

ALWAYS_ALLOWED_ENDPOINTS = []


def has_permission_for_this_operation(
    entity: Union[User, ServiceAccount], operation_id
) -> bool:
    if operation_id in ALWAYS_ALLOWED_ENDPOINTS:
        return entity  # scope check does not apply to always allowed endpoints

    scopes_on_entity = (
        entity.allowed_endpoints.all()
        if hasattr(entity, "allowed_endpoints")
        else entity.endpoint_scopes.all()
    )

    for scope in scopes_on_entity:
        if scope.operation_id == operation_id:
            return entity

    entity_groups = entity.groups.all()
    for group in entity_groups:
        for scope in group.endpoint_scopes.all():
            if scope.operation_id == operation_id:
                return entity

    return False
