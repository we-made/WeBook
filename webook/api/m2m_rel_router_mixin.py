from dataclasses import dataclass
from typing import Dict, List, Tuple, Type

from django.http import Http404
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from ninja.errors import HttpError
from django.db import models

from webook.api.schemas.operation_result_schema import (
    OperationResultSchema,
    OperationResultStatus,
    OperationType,
)


@dataclass
class RelModelDefinition:
    """
    A class that describes a relational model. This class is used to define the relational models that a model may have.
    """

    field_name: str
    relation_model_type: Type[models.Field]

    can_remove: bool = True
    can_add: bool = True
    can_create: bool = True

    can_get: bool = True
    can_list: bool = True

    create_schema: Type[BaseSchema] = None
    get_schema: Type[ModelBaseSchema] = None
    update_schema: Type[BaseSchema] = None
    delete_schema: Type[BaseSchema] = None


class ManyToManyRelRouterMixin:
    """
    Router intended to be used as a mixin for other routers to provide relational functionality.
    For example a model may have notes associated with it. This router provides the ability to create, list, get, and delete notes associated with the model,
    without having to implement the same functionality in multiple routers.

    One should declare the rel_models attribute in the class that inherits from this router. In this attribute you will populate
    the models that you want to associate with the model.
    """

    m2m_rel_fields: Dict[str, Type[models.Field]]

    def init_m2m_functionality(self):
        if self.m2m_rel_fields is None:
            raise HttpError(
                status_code=500,
                message="Relational models must be defined in the m2m_rel_fields attribute. This router uses ManyToManyRelRouterMixin, but does not have any relational models defined.",
            )

        for rel_name, definition in self.m2m_rel_fields.items():
            if definition.can_remove:
                self.add_api_operation(
                    path=f"/{rel_name}/remove",
                    methods=["DELETE"],
                    view_func=self.get_m2m_delete_func(
                        rel_name=rel_name, definition=definition
                    ),
                    response=OperationResultSchema[definition.get_schema],
                    tags=self.tags,
                    auth=self.auth,
                )

            if definition.can_list:
                self.add_api_operation(
                    path=f"/{rel_name}/list",
                    methods=["GET"],
                    view_func=self.get_m2m_list_func(rel_name, definition),
                    response=List[definition.get_schema],
                    tags=self.tags,
                    auth=self.auth,
                )

            if definition.can_add:
                self.add_api_operation(
                    path=f"/{rel_name}/add",
                    methods=["POST"],
                    view_func=self.get_m2m_add_func(rel_name, definition),
                    response=OperationResultSchema[definition.get_schema],
                    tags=self.tags,
                    auth=self.auth,
                )

            if definition.can_create:
                self.add_api_operation(
                    path=f"/{rel_name}/create",
                    methods=["POST"],
                    view_func=self.get_m2m_create_func(rel_name, definition),
                    response=OperationResultSchema[definition.get_schema],
                    tags=self.tags,
                    auth=self.auth,
                )

    def __get_entities(
        self, definition: RelModelDefinition, parent_id: int, related_id: int
    ) -> Tuple[models.Model, models.Model]:
        """Attempt to get the related entity, otherwise raise a 404 error if it does not exist, or is not associated with the parent entity.

        :param definition: The definition of the relational model.
        :param parent_id: The id of the parent model.
        :param related_id: The id of the related model.
        """
        parent_entity = self.model.objects.get(pk=parent_id)
        if parent_entity is None:
            raise Http404(f"{self.model_name_singular} not found")

        if related_id not in parent_entity[definition.field_name]:
            raise Http404(
                f"The given {definition.field_name} is not associated with {self.model_name_singular}"
            )

        related_entity = parent_entity.notes.get(pk=related_id)

        if related_entity is None:
            raise Http404("Note not found")

        return (parent_entity, related_entity)

    def get_m2m_list_func(self, rel_name: str, definition: RelModelDefinition):
        def list_func(request, id: int) -> List[definition.get_schema]:
            """
            Get a list of all instances of the relation model.

            :param id: The id of the parent model.
            """
            return definition.relation_model_type.objects.all()

        return list_func

    def get_m2m_add_func(self, rel_name: str, definition: RelModelDefinition):
        def add_func(
            request, id: int, related_id: int
        ) -> OperationResultSchema[definition.get_schema]:
            """Add an existing instance of the relation model to the parent model."""
            parent_entity = self.model.objects.get(pk=id)

            related_entity = definition.relation_model_type.objects.get(pk=related_id)

            if related_entity is None:
                raise Http404(f"{rel_name} not found")

            parent_entity[definition.field_name].add(related_entity)

            return OperationResultSchema(
                operation=OperationType.ADD,
                status=OperationResultStatus.SUCCESS,
                message=f"{rel_name} added.",
                data=related_entity,
            )

        return add_func

    def get_m2m_create_func(self, rel_name: str, definition: RelModelDefinition):
        def create_func(
            request, payload: definition.create_schema
        ) -> definition.get_schema:
            """Create a new instance of the relation model and add it to the parent model."""
            return definition.create(**payload.dict())

        return create_func

    def get_m2m_delete_func(self, rel_name: str, definition: RelModelDefinition):
        def delete_func(request, id: int, related_id: int):
            """
            Delete the relation model instance.

            :param id: The id of the parent model.
            :param related_id: The id of the relation model instance.
            """
            parent_entity, related_entity = self.__get_entities(
                definition, parent_id=id, related_id=related_id
            )

            parent_entity[definition.field_name].delete(related_id)

            return OperationResultSchema(
                operation=OperationType.REMOVE,
                status=OperationResultStatus.SUCCESS,
                message=f"{rel_name} deleted.",
                data=related_entity,
            )

        return delete_func

    def get_m2m_remove_func(self, rel_name: str, definition: RelModelDefinition):
        def remove_func(request, id: int, related_id: int):
            """Remove the relation model instance from the parent model, but do not delete it."""
            parent_entity, related_entity = self.__get_entities(
                definition, parent_id=id, related_id=related_id
            )

            parent_entity[definition.field_name].remove(related_id)

            return OperationResultSchema(
                operation=OperationType.REMOVE,
                status=OperationResultStatus.SUCCESS,
                message=f"{rel_name} removed.",
                data=related_entity,
            )

        return remove_func
