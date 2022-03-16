# Arrangement Views

# Example:
#from .arrangement_views import (
#   arrangement_create_view
#)

from .arrangement_views import (
  arrangement_detail_view,
  arrangement_list_view,
  arrangement_create_view,
  arrangement_update_view,
  arrangement_delete_view,
)
from .audience_views import (
    audience_detail_view,
    audience_list_view,
    audience_create_view,
    audience_update_view,
    audience_delete_view,
)
from .calendar_views import (
    CalendarSamplesOverview,
    ArrangementCalendarView,
)
from .insight_views import (
    GlobalTimelineView,
)
from .location_views import (
    location_detail_view,
    location_list_view,
    location_create_view,
    location_update_view,
    location_delete_view,
)
