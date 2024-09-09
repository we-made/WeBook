from enum import Enum
from functools import reduce
import inspect
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar
from django.http import HttpResponse
from django.core.paginator import EmptyPage
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.constants import NOT_SET
import pandas as pd
from webook.api.dj_group_auth import SessionGroupAuth
from webook.api.jwt_auth import JWTBearer
from webook.api.paginate import paginate_queryset

from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.api.m2m_rel_router_mixin import ManyToManyRelRouterMixin
from webook.api.schemas.operation_result_schema import (
    OperationResultSchema,
    OperationType,
    OperationResultStatus,
)
import inflect
from django.db import models

from webook.arrangement.models import Person
from webook.utils.camelize import decamelize
from webook.utils.docgen.pdf_gen import TableReport

MAX_PAGE_SIZE = 1000


class Views(Enum):
    CREATE = "create"
    UPDATE = "update"
    GET = "get"
    LIST = "list"
    DELETE = "delete"
    EXPORT = "export"


T = TypeVar("T")

class ExportType(str, Enum):
    """
    The type of export to perform.
    """

    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"


class ExportInstructionSchema(BaseSchema):
    """Instructions for exporting data."""

    """
    Which fields to include in the export.
    If left empty all fields will be included.
    """
    included_fields: Optional[List[str]] = None

    include_archived_entities: bool = False

    """
    Which type of export to perform.
    """
    export_type: ExportType


class ListResponseSchema(BaseSchema, Generic[T]):
    summary: dict
    data: List[T]


class QueryFilter:
    def __init__(
        self,
        param,
        query_by: str,
        default: any = None,
        annotation: Optional[Type] = None,
    ):
        self.param = param
        self.query_by = query_by
        self.default = default
        self.annotation = annotation

    def apply(self, qs, value) -> models.QuerySet:
        return qs.filter(**{self.query_by: value})

    def __str__(self) -> str:
        return f"{self.field}"

class ConditionalCallableTrigger:
    def __init__(
            self,
            param,
            transformer: Callable,
            default: bool = False,
    ):
        self.transformer = transformer
        self.param = param
        self.default = default

    def apply(self, qs, value) -> models.QuerySet:
        return self.transformer(qs, value)
    
    def __str__(self) -> str:
        return f"{self.field}"

class CrudRouter(Router, ManyToManyRelRouterMixin):
    model = None

    auth = None

    views = [
        Views.CREATE, 
        Views.UPDATE, 
        Views.GET, 
        Views.LIST, 
        Views.DELETE,
        Views.EXPORT]

    m2m_rel_fields: Dict[str, Type[models.Field]] = {}

    create_schema = None
    update_schema = None
    get_schema = None
    list_schema = None
    response_schema = None

    create_auth = None
    update_auth = None
    get_auth = None
    list_auth = None

    pre_create_hook: Optional[Callable] = None
    pre_update_hook: Optional[Callable] = None
    pre_delete_hook: Optional[Callable] = None

    non_deferred_fields: List[str] = []

    list_filters: List[QueryFilter] = []

    def __init__(
        self,
        *,
        model: Any,
        auth: Any = NOT_SET,
        tags: Optional[List[str]] = None,
        views: Optional[List[Views]] = None,
        create_auth=None,
        update_auth=None,
        get_auth=None,
        list_auth=None,
        delete_auth=None,
        create_schema=None,
        update_schema=None,
        get_schema=None,
        list_schema=None,
        response_schema=None,
        pre_create_hook: Optional[Callable] = None,
        pre_update_hook: Optional[Callable] = None,
        pre_delete_hook: Optional[Callable] = None,
        export_exclude_fields: Optional[List[str]] = None,
        list_filters: Optional[List[QueryFilter]] = None,
        conditional_callable_triggers: Optional[List[ConditionalCallableTrigger]] = None,
    ) -> None:

        self.property_fields_on_model: List[str] =  [k for k, v in Person.__dict__.items() if type(v) == property]

        self.list_filters += list_filters or []
        self.conditional_callable_triggers: List[ConditionalCallableTrigger] = conditional_callable_triggers or [] 

        self.model = model
        self.model_name_singular = (
            model.entity_name_singular.lower()
            if hasattr(model, "entity_name_singular")
            else model.__name__.lower()
        )
        self.model_name_plural = (
            model.entity_name_plural.lower()
            if hasattr(model, "entity_name_plural")
            else inflect.engine().plural(model.__name__)
        )

        self._deferred_fields = {
            field.name: field
            for field in model._meta.get_fields()
            if field.is_relation and not field.auto_created and not field.name in self.non_deferred_fields
        }

        self.create_auth = create_auth
        self.update_auth = update_auth
        self.get_auth = get_auth
        self.list_auth = list_auth
        self.delete_auth = None

        self.create_schema = create_schema 
        self.update_schema = update_schema
        self.get_schema = get_schema
        self.list_schema = list_schema or self.get_schema
        self.response_schema = response_schema

        self.patch_schema = self.update_schema
        # make all fields optional in patch schema
        if self.patch_schema is not None:
            for field in self.patch_schema.__annotations__.keys():
                setattr(self.patch_schema, field, Optional[self.patch_schema.__annotations__[field]])

        self.pre_create_hook = pre_create_hook
        self.pre_update_hook = pre_update_hook
        self.pre_delete_hook = pre_delete_hook

        self.export_exclude_fields = export_exclude_fields or ["is_archived", "archived_by", "archived_when"]

        super().__init__(auth=auth, tags=tags)

        if views is not None:
            self.views = views

        if Views.CREATE in self.views and self.create_schema is not None:
            self.add_api_operation(
                path="/",
                methods=["POST"],
                auth=self.create_auth or [JWTBearer(), SessionGroupAuth(group_name="planners")],
                view_func=self.get_post_func(),
                response=self.response_schema,
                summary=f"Create {self.model_name_singular}",
                description=f"Create a new {self.model_name_singular.lower()} instance.",
                operation_id=f"create_{self.model_name_singular.lower()}",
                by_alias=True,
            )

        if Views.UPDATE in self.views and self.update_schema is not None:
            self.add_api_operation(
                path="update",
                methods=["PUT"],
                auth=self.update_auth or [JWTBearer(), SessionGroupAuth(group_name="planners")],
                view_func=self.get_put_func(),
                response=OperationResultSchema[self.get_schema],
                summary=f"Update {self.model_name_singular}",
                description=f"Update a {self.model_name_singular.lower()} instance.",
                operation_id=f"update_{self.model_name_singular.lower()}",
                by_alias=True,
            )

            self.add_api_operation(
                path="patch",
                methods=["PATCH"],
                auth=self.update_auth or [JWTBearer(), SessionGroupAuth(group_name="planners")],
                view_func=self.get_put_func(),
                response=OperationResultSchema[self.get_schema],
                summary=f"Patch {self.model_name_singular}",
                description=f"Patch a {self.model_name_singular.lower()} instance.",
                operation_id=f"patch_{self.model_name_singular.lower()}",
                by_alias=True,
            )
        

        if Views.GET in self.views and self.get_schema is not None:
            self.add_api_operation(
                path="get",
                methods=["GET"],
                auth=self.get_auth or self.auth or NOT_SET,
                view_func=self.get_retrieve_func(),
                response=self.get_schema,
                summary=f"Retrieve {self.model_name_singular}",
                description=f"Retrieve a {self.model_name_singular.lower()} instance.",
                operation_id=f"get_{self.model_name_singular.lower()}",
                by_alias=True,
            )

        if Views.LIST in self.views and self.list_schema is not None:
            func = self.get_list_func()

            if self.list_filters or self._deferred_fields:
                """
                There are times when one wants to add extra filter parameters to the list function / endpoint.
                With this setup it has proven somewhat tedious, and the most easy way to do it was by overriding, but there's a lot
                of logic in the list endpoint we don't want the consumer to have to tango with.
                This section is purely to ensure Swagger includes the extra parameters added by the consumer.
                In the get_func method we handle the extras as kwargs, use the QueryFilter instances to apply the filters 
                and return the queryset. This is a much more elegant solution than overriding the list function.

                If you chose to go the override route you would have to:
                    - Consider the parameters that the parent list function takes
                    - Add the parameters you want to add
                    - Call the parent list function
                    - Mutate the queryset some time after get_queryset
                Instead this is how you do it now:
                    - In the consumer, define a new QueryFilter instance
                        -> param: The name of the parameter you want to add
                        -> query_by: The Django query "instruction" (e.g user__groups__name)
                                     TODO: Could this have security implications?
                        -> default: You don't need me to spell this out
                        -> annotation: The type hint of the parameter (important to supply - will be used in Swagger!)

                The way NinjaAPI works is that it uses the signature of the function to generate the Swagger documentation.
                So, we inject the parameters that the consumer wants to add into the signature of the list function, resulting in that
                parameter being hinted in the Swagger documentation.
                """
                sig = inspect.signature(func)

                params = [
                    *list(sig.parameters.values())[
                        :-1
                    ],  # Exclude the variadic keyword parameter
                    *[inspect.Parameter(
                        qf.param,
                        annotation=qf.annotation,
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=qf.default,
                    ) for qf in self.list_filters or []],
                    # *[
                    #     *[inspect.Parameter(
                    #         qf.param,
                    #         annotation=qf.annotation,
                    #         kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    #         default=qf.default,
                    #     )
                    #     for qf in self.list_filters or []],
                    #     *[
                    #         inspect.Parameter(
                    #             "include_" + rel_field,
                    #             annotation=bool,
                    #             kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    #             default=False,
                    #         )
                    #         for rel_field in self._deferred_fields or []
                    #     ]
                    # ],
                    *list(sig.parameters.values())[
                        -1:
                    ],  # Add the variadic keyword parameter at the end
                ]

                func.__signature__ = sig.replace(parameters=params)

            self.add_api_operation(
                path="list",
                methods=["GET"],
                auth=self.list_auth or self.auth or NOT_SET,
                view_func=func,
                response=ListResponseSchema[self.list_schema],
                summary=f"List {self.model_name_plural}",
                description=f"List all {self.model_name_plural.lower()} instances.",
                operation_id=f"list_{self.model_name_plural.lower()}",
                by_alias=True,
            )

            if Views.EXPORT in self.views:
                self.add_api_operation(
                    path="export",
                    methods=["POST"],
                    auth=self.list_auth or self.auth or NOT_SET,
                    view_func=self.get_export_list_func(),
                    response=None,
                    summary=f"Export {self.model_name_plural}",
                    description=f"Export all {self.model_name_plural.lower()} instances.",
                    operation_id=f"export_{self.model_name_plural.lower()}",
                    by_alias=True,
                )

        if Views.DELETE in self.views:
            self.add_api_operation(
                path="delete",
                methods=["DELETE"],
                auth=self.delete_auth or [JWTBearer(), SessionGroupAuth(group_name="planners")],
                view_func=self.get_delete_func(),
                response=OperationResultSchema,
                summary=f"Delete {self.model_name_singular}",
                description=f"Delete a {self.model_name_singular.lower()} instance.",
                operation_id=f"delete_{self.model_name_singular.lower()}",
                by_alias=True,
            )

        self.init_m2m_functionality()

    def get_export_list_func(self):
        def export_func(request, export_instruction: ExportInstructionSchema):
            qs = self.get_queryset()
            if not export_instruction.include_archived_entities and hasattr(self.model, "is_archived"):
                qs = qs.filter(is_archived=False)
            data = self.__transform_data_to_export(qs)

            if export_instruction.export_type == ExportType.CSV:
                response = HttpResponse(content_type="text/csv")
                response["Content-Disposition"] = (
                    f'attachment; filename="{self.model_name_plural}.csv"'
                )

                pd.DataFrame(data).to_csv(
                    response,
                    index=False,
                    sep=";",
                    header=True,
                    encoding="utf-8",
                    quoting=1,
                )

            if export_instruction.export_type == ExportType.EXCEL:
                response = HttpResponse(
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                response["Content-Disposition"] = (
                    f'attachment; filename="{self.model_name_plural}.xlsx"'
                )

                pd.DataFrame(data).to_excel(
                    response, index=False, sheet_name=self.model_name_plural
                )

            if export_instruction.export_type == ExportType.PDF:
                response = HttpResponse("application/pdf")
                response["Content-Disposition"] = (
                    f'attachment; filename="{self.model_name_plural}.pdf"'
                )

                response.write(
                    TableReport(
                        response_or_file_name=response,
                        data=self.__transform_data_to_export(self.model.objects.all()),
                        document_title=self.model_name_plural.replace("_", " ").title(),
                    ).generate()
                )

            return response

        export_func.__name__ = f"export_{self.model_name_plural.lower()}"
        export_func.__doc__ = (
            f"List all {self.model_name_plural.lower()} instances for PDF generation."
        )

        return export_func

    def get_post_func(self):
        def post_func(request, payload: self.create_schema) -> int:
            instance = self.model()

            if self.pre_create_hook is not None:
                (instance, payload) = self.pre_create_hook(instance, payload)

            for key, value in dict(payload).items():
                if value is not NOT_SET:
                    setattr(instance, key, value)

            instance.save()
            return instance

        post_func.__annotations__ = { "payload": self.create_schema, "response": self.model }
        post_func.__name__ = f"create_{self.model_name_singular.lower()}"

        return post_func

    def get_retrieve_func(self):
        def retrieve_func(request, id: int) -> self.get_schema:
            return get_object_or_404(self.model, id=id)

        retrieve_func.__name__ = f"get_{self.model_name_singular.lower()}"

        return retrieve_func

    def __transform_data_to_export(self, data: List) -> List:
        if hasattr(self, "transform_to_export"):
            d = self.transform_to_pdf(self.model.objects.all())
            return d

        d = [x.__dict__ for x in list(self.model.objects.all())]

        private_keys = list(filter(lambda x: x.startswith("_"), d[0].keys()))

        if hasattr(self, "export_exclude_fields"):
            private_keys += self.export_exclude_fields

        for item in d:
            for key in private_keys:
                if key in item:
                    del item[key]

            for key, value in item.copy().items():
                item[key.replace("_", " ").title()] = str(value)
                del item[key]

        return d

    def get_queryset(self):
        manager = self.model.all_objects if hasattr(self.model, "all_objects") else self.model.objects
        return manager.all().defer(
            *self._deferred_fields.keys()
        )        

    def transform_paginator_to_response(self, paginator) -> ListResponseSchema:
        return ListResponseSchema[self.list_schema](
            summary={
                "page": paginator.number,
                "limit": paginator.paginator.per_page,
                "total": paginator.paginator.count,
                "total_pages": paginator.paginator.num_pages,
            },
            data=paginator.object_list
        )

    def apply_filters(self, qs, filters):
        return qs

    def get_list_func(self):
        def list_func(
            request,
            page: int = 0,
            limit: int = 100,
            search: str = None,
            include_archived: bool = False,
            fields_to_search: str = None,
            sort_by: str = None,
            sort_desc: bool = False,
            **extra_params,
        ) -> ListResponseSchema[self.list_schema]:
            qs = self.get_queryset()

            if not include_archived and hasattr(self.model, "is_archived"):
                qs = qs.filter(is_archived=False)

            if limit == 0:
                return HttpResponse("Hi.")

            # Conditional callable triggers allows the subclass to define a param, and a callable that will be triggered
            # if the value of that param is not None. This is useful for when you want to apply a filter to the queryset, but
            # can't use the queryset filter)
            if self.conditional_callable_triggers:
                for cct in self.conditional_callable_triggers:
                    if cct.param in extra_params and extra_params[cct.param] is not None:
                        qs = cct.apply(qs, extra_params[cct.param])        

            if self.list_filters:
                for qf in self.list_filters:
                    if qf.param in extra_params and extra_params[qf.param] is not None:
                        qs = qf.apply(qs, extra_params[qf.param])
            
            if search and fields_to_search:
                fields = [decamelize(x) for x in fields_to_search.split(",")]

                property_fields = []
                normal_fields = []

                prop_qs = None

                for field in fields:
                    if field in self.property_fields_on_model:
                        property_fields.append(field)
                        continue

                    if self.model._meta.get_field(field) is None:
                        raise Exception(f"Field {field} does not exist in {self.model}")
                    
                    normal_fields.append(field)
                    
                if property_fields:
                    objects = list(self.model.objects.all())

                    for field in property_fields:
                        objects = list(filter(
                            lambda o: search.lower() in getattr(o, field).lower(), objects
                        ))

                    prop_qs = qs.filter(id__in=[o.id for o in objects])

                if normal_fields:
                    qs = qs.filter(
                        reduce(
                            lambda x, y: x | y,
                            [
                                models.Q(**{f"{field}__icontains": search})
                                for field in normal_fields
                            ],
                        )
                    )
                    qs = qs.union(prop_qs) if prop_qs else qs

            if sort_by:
                decamalized_sort_by = decamelize(sort_by)
                if decamalized_sort_by in self.property_fields_on_model:
                    items = list(qs.all())
                    items.sort(key=lambda x: getattr(x, decamalized_sort_by), reverse=sort_desc)
                    qs = items
                else:    
                    qs = qs.order_by(f"-{decamalized_sort_by}") if sort_desc else qs.order_by(decamalized_sort_by)
            try:
                paginator = paginate_queryset(qs, page or 1, limit)
            except EmptyPage as e:
                return ListResponseSchema[self.list_schema](
                    summary={
                        "page": page,
                        "limit": limit,
                        "total": 0,
                        "total_pages": 0,
                    },
                    data=[]
                )
            data=paginator.object_list

            response = self.transform_paginator_to_response(paginator)

            return response

        list_func.__name__ = f"list_{self.model_name_plural.lower()}"

        return list_func

    def get_put_func(self):
        def update_func(request, id: int, payload: self.update_schema) -> OperationResultSchema[self.get_schema]:
            instance = get_object_or_404(self.model, id=id)

            if self.pre_update_hook is not None:
                self.pre_update_hook(instance, payload)

            for key, value in dict(payload).items():
                if value is not NOT_SET:
                    if type(value) == list:
                        related_field = getattr(instance, key)
                        related_field.set(value)
                    else:
                        setattr(instance, key, value)
                        
            instance.save()

            return OperationResultSchema[self.get_schema](
                operation=OperationType.UPDATE,
                status=OperationResultStatus.SUCCESS,
                message=f"{self.model_name_singular.lower()} updated successfully",
                data=instance,
            )

        update_func.__name__ = f"update_{self.model_name_singular.lower()}"

        return update_func
    
    def get_patch_func(self):
        def patch_func(request, id: int, payload: self.patch_schema) -> OperationResultSchema[self.get_schema]:
            instance = get_object_or_404(self.model, id=id)

            if self.pre_update_hook is not None:
                self.pre_update_hook(instance, payload)

            for key, value in dict(payload).items():
                if value is not NOT_SET:
                    setattr(instance, key, value)
            instance.save()

            return OperationResultSchema[self.get_schema](
                operation=OperationType.UPDATE,
                status=OperationResultStatus.SUCCESS,
                message=f"{self.model_name_singular.lower()} updated successfully",
                data=instance,
            )
        
        patch_func.__name__ = f"patch_{self.model_name_singular.lower()}"
        
        return patch_func

    def get_delete_func(self):
        def delete_func(request, id: int):
            instance = get_object_or_404(self.model, id=id)

            if self.pre_delete_hook is not None:
                self.pre_delete_hook(instance)

            person = request.user.person

            instance.archive(person)

            return OperationResultSchema[self.get_schema](
                operation=OperationType.DELETE,
                status=OperationResultStatus.SUCCESS,
                message=f"{self.model_name_singular.lower()} deleted successfully",
                data=instance,
            )
        
        delete_func.__name__ = f"delete_{self.model_name_singular.lower()}"

        return delete_func
