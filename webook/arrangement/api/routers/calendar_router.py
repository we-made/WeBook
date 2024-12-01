import json
from dateutil import parser
from typing import List, Optional, Union
from django.db import connection
from ninja import Router
from webook.api.schemas.base_schema import BaseSchema
from webook.api.session_auth import AuthAgent
from webook.arrangement.models import Event
from webook.utils.json_serial import json_serial
from datetime import datetime
from ninja.errors import HttpError

calendar_router = Router(tags=["calendar"])


class CalendarEventSchema(BaseSchema):
    audience_icon: str = ""
    arrangement_name: str = ""
    audience: str = ""
    audience_slug: str = ""
    mainPlannerName: Optional[str] = None
    arrangement_pk: int = 0
    event_pk: int = 0
    slug: str = ""
    name: str = ""
    starts: datetime
    created_when: datetime
    association_type: str = ""
    ends: datetime
    location: str = ""
    location_slug: str = ""
    arrangement_type: str = ""
    arrangement_type_slug: str = ""
    evserie_id: Optional[int] = None
    status_name: Optional[str] = None
    status_color: Optional[str] = None
    status_slug: Optional[str] = None
    expected_visitors: int = 0
    after_buffer_ev_id: Optional[int] = None
    before_buffer_ev_id: Optional[int] = None
    is_rigging: bool = False
    room_names: List[str] = []
    services: List[Union[int, str]] = []
    preconfigurations: List[Union[int, str]] = []
    people_names: List[str] = []
    slug_list: List[str] = []


@calendar_router.get(
    "/arrangementsInPeriod", response={200: List[CalendarEventSchema], 400: str}
)
def get_arrangements_in_period(request, start: str, end: str):
    results = []

    if start and end is None:
        raise Exception("Start and end must be supplied.")

    try:
        start = parser.parse(start).isoformat()
        end = parser.parse(end).isoformat()
    except TypeError:
        raise HttpError("Invalid date format. Please use the format 'YYYY-MM-DD'", 400)

    db_vendor = connection.vendor

    with connection.cursor() as cursor:
        if db_vendor == "postgresql":
            cursor.execute(
                f"""   SELECT audience.icon_class as audience_icon, arr.name as arrangement_name, audience.name as audience, audience.slug as audience_slug, (resp.first_name || ' ' || resp.last_name) as mainPlannerName,
        arr.id as arrangement_pk, ev.id as event_pk, arr.slug as slug, ev.title as name, ev.start as starts, arr.created as created_when, ev.association_type as association_type,
        ev.end as ends, loc.name as location, loc.slug as location_slug, arrtype.name as arrangement_type, arrtype.slug as arrangement_type_slug, evserie.id as evserie_id, status.name as status_name, status.color as status_color,
        status.slug as status_slug, ev.expected_visitors as expected_visitors,
        ev.buffer_after_event_id as after_buffer_ev_id, ev.buffer_before_event_id as before_buffer_ev_id,
        (SELECT EXISTS(SELECT id from arrangement_event WHERE buffer_before_event_id = ev.id OR buffer_after_event_id = ev.id)) AS is_rigging,
        array_agg( DISTINCT room.name) as  room_names,
        array_agg( DISTINCT se.id ) as services,
        array_agg( DISTINCT preconf.id ) as preconfigurations,
        array_agg( DISTINCT participants.first_name || ' ' || participants.last_name ) as people_names,
        (array_to_string(array_agg(DISTINCT room.slug ), ',') || ',' || array_to_string(array_agg(participants.slug), ',')) as slug_list
        from arrangement_arrangement as arr
        JOIN arrangement_event as ev on ev.arrangement_id = arr.id
        JOIN arrangement_location as loc on loc.id = arr.location_id
        LEFT JOIN arrangement_person as resp on resp.id = ev.responsible_id
        LEFT JOIN arrangement_arrangementtype as arrtype on arrtype.id = ev.arrangement_type_id
        LEFT JOIN arrangement_audience as audience on audience.id = ev.audience_id
        LEFT JOIN arrangement_statustype as status on status.id = ev.status_id
        LEFT JOIN arrangement_event_rooms as evr on evr.event_id = ev.id
        LEFT JOIN arrangement_room as room on room.id = evr.room_id
        LEFT JOIN arrangement_serviceorder_events as so_e_link on so_e_link.event_id = ev.id
        LEFT JOIN arrangement_serviceorder as so on so.id = so_e_link.serviceorder_id
        LEFT JOIN arrangement_service as se on se.id = so.service_id
        LEFT JOIN arrangement_serviceorderpreconfiguration as preconf on preconf.id = so.applied_preconfiguration_id
        LEFT JOIN arrangement_serviceorderprovision as sopr on sopr.for_event_id = ev.id
        LEFT JOIN arrangement_serviceorderprovision_selected_personell as s_pers on s_pers.serviceorderprovision_id = sopr.id
        LEFT JOIN arrangement_person as participants on s_pers.person_id = participants.id
        LEFT JOIN arrangement_eventserie as evserie on evserie.id = ev.serie_id
        WHERE arr.is_archived = false AND ev.start > %s AND ev.end < %s AND ev.is_archived = false
        GROUP BY 
            event_pk, audience.icon_class, audience.name, audience.slug,
            resp.first_name, resp.last_name, arr.id, ev.id, arr.slug,
            loc.name, loc.slug, arrtype.name, arrtype.slug, evserie.id,
            status.name, status.color, status.slug, arr.expected_visitors
                            """,
                [start, end],
            )
        elif db_vendor == "sqlite":
            cursor.execute(
                f"""	SELECT audience.icon_class as audience_icon, arr.name as arrangement_name, audience.name as audience, audience.slug as audience_slug, resp.first_name || " " || resp.last_name as mainPlannerName,
                            arr.id as arrangement_pk, ev.id as event_pk, arr.slug as slug, ev.title as name, ev.start as starts, arr.created as created_when, ev.association_type as association_type,
                            ev.end as ends, loc.name as location, loc.slug as location_slug, arrtype.name as arrangement_type, arrtype.slug as arrangement_type_slug, evserie.id as evserie_id, status.name as status_name, status.color as status_color,
                            ev.buffer_after_event_id as after_buffer_ev_id, ev.buffer_before_event_id as before_buffer_ev_id,
                            (SELECT EXISTS(SELECT id from arrangement_event WHERE buffer_before_event_id = ev.id OR buffer_after_event_id = ev.id)) AS is_rigging,
                            GROUP_CONCAT( DISTINCT room.name) as room_names, 
                            GROUP_CONCAT( DISTINCT participants.first_name || " " || participants.last_name ) as people_names,
                            GROUP_CONCAT(DISTINCT room.slug ) || "," || GROUP_CONCAT(DISTINCT participants.slug) as slug_list
                            from arrangement_arrangement as arr 
                            JOIN arrangement_arrangementtype as arrtype on arrtype.id = arr.arrangement_type_id
                            JOIN arrangement_location as loc on loc.id = arr.location_id
                            JOIN arrangement_person as resp on resp.id = arr.responsible_id
                            JOIN arrangement_audience as audience on audience.id = arr.audience_id
                            JOIN arrangement_event as ev on ev.arrangement_id = arr.id
                            left join arrangement_statustype as status on status.id = ev.status_id
                            LEFT JOIN arrangement_event_people as evp on evp.event_id = ev.id
                            LEFT JOIN arrangement_person as participants on participants.id = evp.person_id
                            LEFT JOIN arrangement_event_rooms as evr on evr.event_id = ev.id
                            LEFT JOIN arrangement_room as room on room.id = evr.room_id
                            LEFT JOIN arrangement_eventserie as evserie on evserie.id = ev.serie_id
                            WHERE arr.is_archived = 0 AND ev.start > %s AND ev.end < %s AND ev.is_archived = 0
                            GROUP BY event_pk""",
                [start, end],
            )
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            m = dict(zip(columns, row))

            m["room_names"] = [x for x in m["room_names"] if x is not None]
            m["services"] = [x for x in m["services"] if x is not None]
            m["preconfigurations"] = [
                x for x in m["preconfigurations"] if x is not None
            ]
            m["people_names"] = [x for x in m["people_names"] if x is not None]

            m["slug_list"] = (
                m["slug_list"].split(",") if m["slug_list"] is not None else []
            )
            if db_vendor == "sqlite":
                m["room_names"] = (
                    m["room_names"].split(",") if m["room_names"] is not None else []
                )
                m["people_names"] = (
                    m["people_names"].split(",")
                    if m["people_names"] is not None
                    else []
                )
            results.append(m)

    return results
