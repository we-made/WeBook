from __future__ import annotations
from typing import List, Optional, Union
from webook.api.routers.service_account_router import ServiceAccountSchema
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.api.schemas import AudienceGetSchema, LocationGetSchema
from webook.onlinebooking.models import OnlineBookingSettings


class CitySegmentCreateSchema(BaseSchema):
    name: str
    county_id: int


# Ensure that this comes BEFORE CountyGetSchema or you will get weird Pydantic serialization errors.
class CitySegmentGetSchema(ModelBaseSchema, CitySegmentCreateSchema):
    pass


class CountyCreateSchema(BaseSchema):
    name: str
    county_number: int
    city_segment_enabled: bool
    school_enabled: bool


class CountyGetSchema(ModelBaseSchema, CountyCreateSchema):
    city_segments: Optional[List[CitySegmentGetSchema]] = None


class SchoolCreateSchema(BaseSchema):
    name: str
    county_id: int
    city_segment_id: Optional[int]
    audiences: List[int] = []


class SchoolGetSchema(ModelBaseSchema, SchoolCreateSchema):
    audiences: List[AudienceGetSchema] = []


class OnlineBookingCreateSchema(BaseSchema):
    county_id: int
    school_id: Optional[int]
    visitors_count: int
    audience_type_id: int


class OnlineBookingGetSchema(ModelBaseSchema, OnlineBookingCreateSchema):
    school: Optional[SchoolGetSchema] = None
    segment: Optional[CitySegmentGetSchema] = None
    audience_type: AudienceGetSchema
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    service_account: Optional[ServiceAccountSchema] = None


class OnlineBookingSettingsGetSchema(BaseSchema):
    title_format: str
    allowed_audiences: List[AudienceGetSchema]

    location: Optional[LocationGetSchema]
    location_id: Optional[int]

    main_planner_id: Optional[int]
    status_type_id: Optional[int]
    arrangement_type_id: Optional[int]

    offset_unit: OnlineBookingSettings.Unit
    offset: int
    duration_unit: OnlineBookingSettings.Unit
    duration_amount: int


class OnlineBookingSettingsUpdateSchema(BaseSchema):
    title_format: Optional[str]
    allowed_audiences: Optional[List[int]]
    location_id: Optional[int]
    main_planner_id: Optional[int]
    status_type_id: Optional[int]
    arrangement_type_id: Optional[int]
    offset_unit: Optional[OnlineBookingSettings.Unit]
    offset: Optional[int]
    duration_unit: Optional[OnlineBookingSettings.Unit]
    duration_amount: Optional[int]
