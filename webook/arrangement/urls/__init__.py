from .arrangement_urls import arrangement_urls
from .audience_urls import audience_urls
from .calendar_urls import calendar_urls
from .dashboard_urls import dashboard_urls
from .insights_urls import insights_urls
from .location_urls import location_urls
from .organization_urls import organization_urls
from .organizationtype_urls import organizationtype_urls
from .person_urls import person_urls
from .room_urls import room_urls
from .servicetype_urls import servicetype_urls
from .statistics_urls import statistics_urls


app_name = "arrangement"

urlpatterns = []
urlpatterns.extend(arrangement_urls)
urlpatterns.extend(audience_urls)
urlpatterns.extend(calendar_urls)
urlpatterns.extend(dashboard_urls)
urlpatterns.extend(insights_urls)
urlpatterns.extend(location_urls)
urlpatterns.extend(organization_urls)
urlpatterns.extend(organizationtype_urls)
urlpatterns.extend(person_urls)
urlpatterns.extend(room_urls)
urlpatterns.extend(servicetype_urls)
urlpatterns.extend(statistics_urls)