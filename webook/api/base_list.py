from functools import reduce
from typing import Any, List, Optional

from webook.api.crud_router import ConditionalCallableTrigger, QueryFilter
from django.db.models import Model

from webook.api.paginate import paginate_queryset
from webook.arrangement import models
from webook.utils.camelize import decamelize


class ListApiMethod:
    query_filters: List[QueryFilter] = []
    model: Optional[Model] = None

    def __init__(
        self,
        query_filters: List[QueryFilter] = [],
        conditional_callable_triggers: List[ConditionalCallableTrigger] = [],
        model: Optional[Model] = None,
    ):
        self.query_filters = query_filters
        self.conditional_callable_triggers = conditional_callable_triggers
        self.model = model

    def marshall_data(
        self,
        page: int = 1,
        limit: int = 100,
        search: str = None,
        include_archived: bool = False,
        fields_to_search: str = None,
        sort_by: str = None,
        sort_desc: bool = False,
        **extra_params: Any,
    ) -> Any:
        qs = self.get_queryset()

        if not include_archived:
            qs = qs.filter(archived=False)

        # Conditional callable triggers allows the subclass to define a param, and a callable that will be triggered
        # if the value of that param is not None. This is useful for when you want to apply a filter to the queryset, but
        # can't use the queryset filter)
        if self.conditional_callable_triggers:
            for cct in self.conditional_callable_triggers:
                if cct.param in extra_params and extra_params[cct.param] is not None:
                    qs = cct.apply(qs, extra_params[cct.param])

        if self.query_filters:
            for qf in self.query_filters:
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
                    objects = list(
                        filter(
                            lambda o: search.lower() in getattr(o, field).lower(),
                            objects,
                        )
                    )

                prop_qs = qs.filter(id__in=[o.id for o in objects])

            if normal_fields:
                qs = self.model.objects.filter(
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
            qs = qs.order_by(f"-{sort_by}") if sort_desc else qs.order_by(sort_by)

        paginator = paginate_queryset(qs, page, limit)

        return self.transform_paginator_to_response(paginator)

    def get_queryset(self):
        if self.model is None:
            raise NotImplementedError(
                "Model is not defined. Set a model or override get_queryset method."
            )

        return self.model.objects.all()

    def __call__(
        self,
        page: int = 1,
        limit: int = 100,
        search: str = None,
        include_archived: bool = False,
        fields_to_search: str = None,
        sort_by: str = None,
        sort_desc: bool = False,
        **extra_params: Any,
    ) -> Any:
        return self.marshall_data(
            page=page,
            limit=limit,
            search=search,
            include_archived=include_archived,
            fields_to_search=fields_to_search,
            sort_by=sort_by,
            sort_desc=sort_desc,
            **extra_params,
        )
