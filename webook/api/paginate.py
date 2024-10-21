from dataclasses import dataclass
import inspect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .standards import MAX_PAGE_SIZE, STANDARD_PAGE_SIZE
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, Page
from django.utils.inspect import method_has_no_args
from django.utils.functional import cached_property


# class AsyncPaginator(Paginator):
#     @cached_property
#     async def count(self):
#         """Return the total number of objects, across all pages."""
#         c = getattr(self.object_list, "acount", None)
#         if callable(c) and not inspect.isbuiltin(c) and method_has_no_args(c):
#             return await c()
#         return len(self.object_list)


@dataclass
class PaginatedData:
    paginated_qs: QuerySet
    page_size: int
    total_items: int
    current_page: int
    num_pages: int


async def paginate_queryset(
    queryset, page, page_size: int = STANDARD_PAGE_SIZE
) -> PaginatedData:
    """Paginate a queryset and return the paginated queryset."""
    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE

    if isinstance(queryset, QuerySet) and not queryset.ordered:
        queryset = queryset.order_by("id")

    count = await queryset.acount()
    qs = queryset[(page - 1) * page_size : min(page * page_size, count)]

    pd = PaginatedData(
        paginated_qs=qs,
        page_size=page_size,
        total_items=count,
        current_page=page,
        num_pages=count // page_size + 1,
    )

    return pd

    # paginator = Paginator(queryset, page_size)

    # try:
    #     paginated_queryset = paginator.page(page)
    # except PageNotAnInteger:
    #     paginated_queryset = paginator.page(1)

    # return paginated_queryset
