from webook.arrangement.views import room_preset_views

from .analysis_urls import analysis_urls
from .arrangement_type_urls import arrangement_type_urls
from .arrangement_urls import arrangement_urls
from .audience_urls import audience_urls
from .calendar_urls import calendar_urls
from .confirmation_urls import confirmation_urls
from .dashboard_urls import dashboard_urls
from .event_serie_urls import event_serie_urls
from .event_urls import event
from .insights_urls import insights_urls
from .location_urls import location_urls
from .note_urls import note_urls
from .organization_urls import organization_urls
from .organizationtype_urls import organizationtype_urls
from .person_urls import person_urls
from .planner_urls import planner_urls
from .requisition_urls import requisition_urls
from .room_preset_urls import room_preset_urls
from .room_urls import room_urls
from .servicetype_urls import servicetype_urls

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
urlpatterns.extend(planner_urls)
urlpatterns.extend(note_urls)
urlpatterns.extend(requisition_urls)
urlpatterns.extend(confirmation_urls)
urlpatterns.extend(arrangement_type_urls)
urlpatterns.extend(room_preset_urls)
urlpatterns.extend(event_serie_urls)
urlpatterns.extend(analysis_urls)
urlpatterns.extend(event_urls)
