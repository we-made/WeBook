"""event_queries.py

This file contains queries that are used to get events from the database.
Used in calendar views.

"""

import json
from datetime import datetime
from typing import List, Optional, Tuple

from dateutil import parser
from django.db import connection

from webook.utils import json_serial


def __arrangement_query_builder(where: str):
    """
    Builds a query that returns all arrangements that are not archived

    Args:
        where: A string that is used to filter the query.

    Returns:
        A string that is a query. Remember to parameterize this string, do not pass values in directly with the where argument.
    """
    if connection.vendor == "postgresql":
        return f"""
        SELECT audience.icon_class as audience_icon, arr.name as arrangement_name, audience.name as audience, audience.slug as audience_slug, (resp.first_name || ' ' || resp.last_name) as mainPlannerName,
                                arr.id as arrangement_pk, ev.id as event_pk, arr.slug as slug, ev.title as name, ev.start as starts, arr.created as created_when, ev.association_type as association_type,
                                ev.end as ends, loc.name as location, loc.slug as location_slug, arrtype.name as arrangement_type, arrtype.slug as arrangement_type_slug, evserie.id as evserie_id, status.name as status_name, status.color as status_color,
                                status.slug as status_slug, ev.expected_visitors as expected_visitors,
                                ev.buffer_after_event_id as after_buffer_ev_id, ev.buffer_before_event_id as before_buffer_ev_id,
                                (SELECT EXISTS(SELECT id from arrangement_event WHERE buffer_before_event_id = ev.id OR buffer_after_event_id = ev.id)) AS is_rigging,
                                array_agg( DISTINCT room.name) as room_names,
                                array_agg( DISTINCT participants.first_name || ' ' || participants.last_name ) as people_names,
                                (array_to_string(array_agg(DISTINCT room.slug ), ',') || ',' || array_to_string(array_agg(DISTINCT participants.slug), ',')) as slug_list
                                from arrangement_arrangement as arr
                                JOIN arrangement_event as ev on ev.arrangement_id = arr.id
                                JOIN arrangement_location as loc on loc.id = arr.location_id
                                LEFT JOIN arrangement_person as resp on resp.id = ev.responsible_id
                                LEFT JOIN arrangement_arrangementtype as arrtype on arrtype.id = ev.arrangement_type_id
                                LEFT JOIN arrangement_audience as audience on audience.id = ev.audience_id
                                LEFT JOIN arrangement_statustype as status on status.id = ev.status_id
                                LEFT JOIN arrangement_event_people as evp on evp.event_id = ev.id
                                LEFT JOIN arrangement_person as participants on participants.id = evp.person_id
                                LEFT JOIN arrangement_event_rooms as evr on evr.event_id = ev.id
                                LEFT JOIN arrangement_room as room on room.id = evr.room_id
                                LEFT JOIN arrangement_eventserie as evserie on evserie.id = ev.serie_id
                                WHERE {where} AND ev.is_archived = false
                                GROUP BY 
                                    event_pk, audience.icon_class, audience.name, audience.slug,
                                    resp.first_name, resp.last_name, arr.id, ev.id, arr.slug,
                                    loc.name, loc.slug, arrtype.name, arrtype.slug, evserie.id,
                                    status.name, status.color, status.slug, arr.expected_visitors
                                """
    elif connection.vendor == "sqlite":
        return f"""
                    SELECT audience.icon_class as audience_icon, arr.name as arrangement_name, audience.name as audience, audience.slug as audience_slug, resp.first_name || " " || resp.last_name as mainPlannerName,
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
                            WHERE {where} AND ev.is_archived = 0
                            GROUP BY event_pk
                """


def __parse_results(cursor) -> List[dict]:
    """Parse results from query and return a list of dictionaries"""
    results = []
    columns = [column[0] for column in cursor.description]

    for row in cursor.fetchall():
        m = dict(zip(columns, row))

        m["slug_list"] = m["slug_list"].split(",") if m["slug_list"] is not None else []
        if connection.vendor == "sqlite":
            m["room_names"] = (
                m["room_names"].split(",") if m["room_names"] is not None else []
            )
            m["people_names"] = (
                m["people_names"].split(",") if m["people_names"] is not None else []
            )
        results.append(m)

    return results


def __parse_datetimes(start: str, end: str) -> Tuple[datetime]:
    if start and end is None:
        raise Exception("Start and end must be supplied.")

    try:
        start = parser.parse(start).isoformat()
        end = parser.parse(end).isoformat()
    except TypeError:
        raise Exception("Start and end must be datetime objects.")

    return start, end


def get_arrangements_in_period(start: datetime, end: datetime) -> List[dict]:
    start, end = __parse_datetimes(start, end)
    with connection.cursor() as cursor:
        cursor.execute(
            __arrangement_query_builder("ev.start > %s AND ev.end < %s"),
            [start, end],
        )

        return __parse_results(cursor)


def get_arrangements_in_period_for_person(
    start: datetime, end: datetime, person_id: int
) -> List[dict]:
    """Get all arrangements in a period for a given person"""
    if start is None:
        return []
    start, end = __parse_datetimes(start, end)
    with connection.cursor() as cursor:
        cursor.execute(
            __arrangement_query_builder(
                "ev.start > %s AND ev.end < %s AND evp.person_id = %s"
            ),
            [start, end, person_id],
        )

        return __parse_results(cursor)
