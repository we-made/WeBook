from typing import Optional
from ninja import Router

from webook.api.crud_router import CrudRouter, QueryFilter, Views
from webook.api.jwt_auth import JWTBearer
from webook.arrangement.models import Audience
from webook.onlinebooking.api.schemas import (
    OnlineBookingCreateSchema,
    OnlineBookingGetSchema,
    OnlineBookingSettingsGetSchema,
    OnlineBookingSettingsUpdateSchema,
)
from webook.onlinebooking.models import (
    CitySegment,
    OnlineBooking,
    OnlineBookingSettings,
    School,
)


class OnlineBookingRouter(CrudRouter):
    def __init__(self, *args, **kwargs):
        self.list_filters = [
            QueryFilter(
                param="county_id",
                query_by="school__county__id",
                default=None,
                annotation=Optional[int],
            ),
            QueryFilter(
                param="school_id",
                query_by="school__id",
                default=None,
                annotation=Optional[int],
            ),
            QueryFilter(
                param="city_segment_id",
                query_by="school__city_segment__id",
                default=None,
                annotation=Optional[int],
            ),
        ]

        super().__init__(*args, **kwargs)


online_booking_router = OnlineBookingRouter(
    model=OnlineBooking,
    tags=["Online Booking"],
    views=[Views.GET, Views.LIST, Views.DELETE],
    get_schema=OnlineBookingGetSchema,
)


@online_booking_router.post("/create", response=OnlineBookingGetSchema)
def create_online_booking(
    request, payload: OnlineBookingCreateSchema
) -> OnlineBookingGetSchema:
    ob = OnlineBooking()
    try:
        ob.school = School.objects.get(id=payload.school_id)
    except School.DoesNotExist:
        return {"message": "School not found."}

    if ob.school.county.city_segment_enabled:
        if not payload.segment_id and not payload.segment_text:
            return {"message": "City segment is required for this school."}
        if payload.segment_id:
            try:
                ob.segment = ob.school.county.city_segments.get(id=payload.segment_id)
            except CitySegment.DoesNotExist:
                return {"message": "City segment not found."}
        else:
            ob.segment_text = payload.segment_text

    try:
        ob.audience_type = Audience.objects.get(id=payload.audience_type_id)
    except Audience.DoesNotExist:
        return {"message": "Audience type not found."}

    ob.visitors_count = payload.visitors_count

    ob.ip_address = (
        request.headers.get("x-forwarded-for")
        if request.headers.get("x-forwarded-for")
        else None
    )
    ob.user_agent = request.headers.get("user-agent")

    ob.save()

    return ob


@online_booking_router.get("/settings", response=OnlineBookingSettingsGetSchema)
def get_online_booking_settings(request) -> OnlineBookingSettingsGetSchema:
    settings = OnlineBookingSettings.objects.first()
    if settings is None:
        settings = OnlineBookingSettings.objects.create()
        settings.save()

    return settings


@online_booking_router.put("/settings/update", response=OnlineBookingSettingsGetSchema)
def update_online_booking_settings(
    request, payload: OnlineBookingSettingsUpdateSchema
) -> OnlineBookingGetSchema:
    settings = OnlineBookingSettings.objects.first()
    if not settings:
        return {"message": "No settings found."}

    for audience_id in payload.allowed_audiences:
        try:
            settings.allowed_audiences.add(Audience.objects.get(id=audience_id))
        except Audience.DoesNotExist:
            return {"message": "Audience not found."}

    settings.offset_unit = payload.offset_unit or OnlineBookingSettings.Unit.MINUTES
    settings.offset = payload.offset or 0
    settings.duration_unit = payload.duration_unit or OnlineBookingSettings.Unit.MINUTES
    settings.duration_amount = payload.duration_amount or 15

    settings.save()

    return settings
