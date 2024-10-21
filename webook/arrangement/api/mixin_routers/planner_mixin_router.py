from typing import List, Type
from django.shortcuts import get_object_or_404
from webook.api.schemas.base_schema import BaseSchema
from webook.api.schemas.operation_result_schema import (
    OperationResultSchema,
    OperationResultStatus,
    OperationType,
)
from webook.arrangement.api.mixin_routers.base_mixin_router import BaseMixinRouter
from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.arrangement.models import BaseFileRelAbstractModel, Person
from ninja.errors import HttpError
from datetime import datetime


class PlannerMixinRouter(BaseMixinRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_api_operation(
            path="/planner/list",
            methods=["GET"],
            view_func=self.PlannerFunctionality.get_list_planner_func(
                router_instance=self
            ),
            response=List[PersonGetSchema],
            tags=self.tags,
            auth=self.auth,
            operation_id="list_planners_of_" + self.model_name_singular.lower(),
            summary="List all planners of " + self.model_name_singular.lower(),
            description="List all planners of the " + self.model_name_singular.lower(),
            by_alias=True,
        )

        self.add_api_operation(
            path="/planner/add",
            methods=["POST"],
            view_func=self.PlannerFunctionality.get_add_planner_func(
                router_instance=self
            ),
            response=OperationResultSchema[PersonGetSchema],
            tags=self.tags,
            auth=self.auth,
            operation_id="add_planner_to_" + self.model_name_singular.lower(),
            summary="Add a planner",
            description="Add a planner to the "
            + self.model_name_singular.lower()
            + " entity",
            by_alias=True,
        )

        self.add_api_operation(
            path="/planner/remove",
            methods=["DELETE"],
            view_func=self.PlannerFunctionality.get_remove_planner_func(
                router_instance=self
            ),
            response=OperationResultSchema[PersonGetSchema],
            tags=self.tags,
            auth=self.auth,
            operation_id="remove_planner_from_" + self.model_name_singular.lower(),
            summary="Remove a planner",
            description="Remove a planner from the "
            + self.model_name_singular.lower()
            + " entity",
            by_alias=True,
        )

    class PlannerFunctionality:
        @staticmethod
        def get_list_planner_func(router_instance):
            def list_planner_func(request, parent_entity_id: int):
                parent_entity = get_object_or_404(
                    router_instance.model, pk=parent_entity_id
                )
                return parent_entity.planners.all()

            return list_planner_func

        @staticmethod
        def get_add_planner_func(router_instance):
            def add_planner_func(request, parent_entity_id: int, planner_id: int):
                planner_person = get_object_or_404(Person, pk=planner_id)

                parent_entity = get_object_or_404(
                    router_instance.model, pk=parent_entity_id
                )
                parent_entity.planners.add(planner_person)
                return OperationResultSchema[PersonGetSchema](
                    status=OperationResultStatus.SUCCESS,
                    operation=OperationType.CREATE,
                    message=f"Planner {planner_person} added to {parent_entity}",
                    data=planner_person,
                )

            return add_planner_func

        @staticmethod
        def get_remove_planner_func(router_instance):
            def remove_planner_func(request, parent_entity_id: int, planner_id: int):
                planner_person = get_object_or_404(Person, pk=planner_id)

                parent_entity = get_object_or_404(
                    router_instance.model, pk=parent_entity_id
                )
                parent_entity.planners.remove(planner_person)
                return OperationResultSchema[PersonGetSchema](
                    status=OperationResultStatus.SUCCESS,
                    operation=OperationType.DELETE,
                    message=f"Planner {planner_person} removed from {parent_entity}",
                    data=planner_person,
                )

            return remove_planner_func
