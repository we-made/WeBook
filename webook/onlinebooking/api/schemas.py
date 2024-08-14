from __future__ import annotations
from typing import List, Optional
from webook.api.routers.service_account_router import ServiceAccountSchema
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.api.schemas import AudienceGetSchema
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


class CountyGetSchema(ModelBaseSchema, CountyCreateSchema):
    city_segments: Optional[List[CitySegmentGetSchema]] = None


class SchoolCreateSchema(BaseSchema):
    name: str
    county_id: int
    audience_id: Optional[int]
    city_segment_id: Optional[int]


class SchoolGetSchema(ModelBaseSchema, SchoolCreateSchema):
    county: CountyGetSchema
    audience: Optional[AudienceGetSchema]
    city_segment: Optional[CitySegmentGetSchema]


class OnlineBookingCreateSchema(BaseSchema):
    school_id: int

    segment_id: Optional[int] = None
    segment_text: Optional[str] = None

    visitors_count: int
    audience_type_id: int


class OnlineBookingGetSchema(ModelBaseSchema, OnlineBookingCreateSchema):
    school: SchoolGetSchema
    segment: Optional[CitySegmentGetSchema] = None
    audience_type: AudienceGetSchema
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    service_account: Optional[ServiceAccountSchema] = None


class OnlineBookingSettingsGetSchema(BaseSchema):
    title_format: str
    allowed_audiences: List[AudienceGetSchema]
    offset_unit: OnlineBookingSettings.Unit
    offset: int
    duration_unit: OnlineBookingSettings.Unit
    duration_amount: int


class OnlineBookingSettingsUpdateSchema(BaseSchema):
    title_format: Optional[str]
    allowed_audiences: Optional[List[int]]
    offset_unit: Optional[OnlineBookingSettings.Unit]
    offset: Optional[int]
    duration_unit: Optional[OnlineBookingSettings.Unit]
    duration_amount: Optional[int]
