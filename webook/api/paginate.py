from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .standards import MAX_PAGE_SIZE, STANDARD_PAGE_SIZE
from django.db.models.query import QuerySet


def paginate_queryset(queryset, page, page_size: int = STANDARD_PAGE_SIZE) -> Paginator:
    """Paginate a queryset and return the paginated queryset."""
    if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE

    if isinstance(queryset, QuerySet) and not queryset.ordered:
        queryset = queryset.order_by("id")

    paginator = Paginator(queryset, page_size)

    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)

    return paginated_queryset
