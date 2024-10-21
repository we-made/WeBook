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

from webook.screenshow.api import (
    DisplayLayoutSettingGetSchema,
    ScreenGroupGetSchema,
    ScreenResourceGetSchema,
)
from webook.screenshow.models import DisplayLayout


class DisplayLayoutGetSchema(BaseSchema):
    id: int
    name: str
    description: str = ""
    items_shown: int
    is_room_based: bool = True
    is_active: bool = True

    triggers_display_layout_text: bool = False

    screens: List[ScreenResourceGetSchema]
    groups: List[ScreenGroupGetSchema]

    setting: DisplayLayoutSettingGetSchema

    slug: str

    created: datetime
    modified: datetime


class DisplayLayoutMixinRouter(BaseMixinRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_api_operation(
            path="/displayLayouts/list",
            methods=["GET"],
            view_func=self.DisplayLayoutFunctionality.get_list_display_layouts_func(
                router_instance=self
            ),
            response=List[PersonGetSchema],
            tags=self.tags,
            auth=self.auth,
            operation_id="list_display_layouts",
            summary="List all display layouts",
            description="List all display layouts",
            by_alias=True,
        )

        self.add_api_operation(
            path="/displayLayouts/add",
            methods=["POST"],
            view_func=self.DisplayLayoutFunctionality.get_add_display_layout_func(
                router_instance=self
            ),
            response=OperationResultSchema[PersonGetSchema],
            tags=self.tags,
            auth=self.auth,
            operation_id="add_display_layout_to_" + self.model_name_singular.lower(),
            summary="Add a display layout",
            description="Add a display layout to the "
            + self.model_name_singular.lower()
            + " entity",
            by_alias=True,
        )

        self.add_api_operation(
            path="/displayLayouts/remove",
            methods=["DELETE"],
            view_func=self.DisplayLayoutFunctionality.get_remove_display_layout_func(
                router_instance=self
            ),
            response=OperationResultSchema[PersonGetSchema],
            tags=self.tags,
            auth=self.auth,
            operation_id="remove_display_layout_from_"
            + self.model_name_singular.lower(),
            summary="Remove a display layout",
            description="Remove a display layout from the "
            + self.model_name_singular.lower()
            + " entity",
            by_alias=True,
        )

    class DisplayLayoutFunctionality:
        @staticmethod
        def get_list_display_layouts_func(router_instance):
            def list_display_layouts_func(request, parent_entity_id: int):
                parent_entity = get_object_or_404(
                    router_instance.model, pk=parent_entity_id
                )
                return parent_entity.display_layouts.all()

            return list_display_layouts_func

        @staticmethod
        def get_add_display_layout_func(router_instance):
            def add_display_layout_func(
                request, parent_entity_id: int, display_layout_id: int
            ):
                display_layout = get_object_or_404(DisplayLayout, pk=display_layout_id)

                parent_entity = get_object_or_404(
                    router_instance.model, pk=parent_entity_id
                )
                parent_entity.display_layouts.add(display_layout)
                return OperationResultSchema[PersonGetSchema](
                    status=OperationResultStatus.SUCCESS,
                    operation=OperationType.CREATE,
                    message=f"Display Layout {display_layout} added to {parent_entity}",
                    data=display_layout,
                )

            return add_display_layout_func

        @staticmethod
        def get_remove_display_layout_func(router_instance):
            def remove_display_layout_func(
                request, parent_entity_id: int, display_layout_id: int
            ):
                display_layout = get_object_or_404(DisplayLayout, pk=display_layout_id)

                parent_entity = get_object_or_404(
                    router_instance.model, pk=parent_entity_id
                )
                parent_entity.display_layouts.remove(display_layout)
                return OperationResultSchema[PersonGetSchema](
                    status=OperationResultStatus.SUCCESS,
                    operation=OperationType.DELETE,
                    message=f"Display Layout {display_layout} removed from {parent_entity}",
                    data=display_layout,
                )

            return remove_display_layout_func
