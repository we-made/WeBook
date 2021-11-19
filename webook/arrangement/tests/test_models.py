import pytest

from datetime import (
    datetime,
    time,
)

from webook.arrangement.models import (
    Arrangement,
    Article,
    Audience,
    BusinessHour,
    Location,
    OrganizationType,
    Room,
    ServiceType,
    TimelineEvent,
)

def test_audience__str__():
    audience = Audience()
    audience.name = "test"
    assert audience.__str__() == "test"
    assert str(audience) == "test"

def test_arrangement__str__():
    arrangement = Arrangement()
    arrangement.name = "test"
    assert arrangement.__str__() == "test"
    assert str(arrangement) == "test"

def test_location__str__():
    location = Location()
    location.name = "test"
    assert location.__str__() == "test"
    assert str(location) == "test"

def test_room__str__():
    room = Room()
    room.name = "test"
    assert room.__str__() == "test"
    assert str(room) == "test"

def test_article__str__():
    article = Article()
    article.name = "test"
    assert article.__str__() == "test"
    assert str(article) == "test"

def test_organization_type__str__():
    organization_type = OrganizationType()
    organization_type.name = "test"
    assert organization_type.__str__() == "test"
    assert str(organization_type) == "test"

def test_timeline_event__str__():
    timeline_event = TimelineEvent()
    timeline_event.content = "test"
    assert timeline_event.__str__() == "test"
    assert str(timeline_event) == "test"

def test_service_type__str__():
    service_type = ServiceType()
    service_type.name = "test"
    assert service_type.__str__() == "test"
    assert str(service_type) == "test"

def test_business_hour__str__():
    business_hour = BusinessHour()
    business_hour.start_of_business_hours = time(7, 0)
    business_hour.end_of_business_hours = time(14, 0) 
    assert business_hour.__str__() == "07:00 - 14:00"
    assert str(business_hour) == "07:00 - 14:00"