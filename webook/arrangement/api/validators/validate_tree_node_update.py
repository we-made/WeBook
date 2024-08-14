from typing import Tuple, Type

from django.http import Http404, HttpResponseBadRequest
from webook.api.schemas.base_schema import BaseSchema
from webook.arrangement.models import SelfNestedModelMixin
from ninja.errors import HttpError


def validate_tree_node_update(
    model: Type[SelfNestedModelMixin],
    instance: SelfNestedModelMixin,
    payload: BaseSchema,
) -> Tuple[SelfNestedModelMixin, dict]:
    """Validate the node type instance"""
    if not hasattr(payload, "parent_id"):
        return instance, payload

    if payload.parent_id is not None and payload.parent_id > 0:
        if payload.parent_id == instance.id:
            raise HttpError(
                status_code=400,
                message="Parent node cannot be the same as the node",
            )

        parent_node = model.objects.get(id=payload.parent_id)

        if parent_node is None:
            raise Http404("Parent node by id '%s' does not exist" % payload.parent_id)

        if parent_node.parent_id == instance.id:
            raise HttpError(
                status_code=400,
                message="Parent node cannot be the same as the node's parent",
            )

        instance.parent = parent_node
    else:
        instance.parent = None

    return instance, payload
