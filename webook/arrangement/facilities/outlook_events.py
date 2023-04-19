from datetime import datetime

from django.conf import settings

from api_client.webook_api_client import WebookAPIClient
from webook.arrangement.models import Person

api_client = WebookAPIClient(
    api_url=settings.API_URL,
    user_name=settings.API_USER_NAME,
    password=settings.API_USER_PASSWORD,
)


def get_outlook_events_for_person(person: Person, start: datetime, end: datetime):
    """Query the WeBook API for Outlook events for the given person"""
    if person.social_provider_id is None:
        return []

    get_events_response = api_client.httpx_client.get(
        f"/v1/outlook/{person.social_provider_id}?start_datetime_iso_8601={start.isoformat()}&end_datetime_iso_8601={end.isoformat()}"
    )

    outlook_events = get_events_response.json()

    events = list(
        map(
            lambda o_event: {
                "id": o_event["id"],
                "title": o_event["subject"],
                "start": o_event["start"]["dateTime"],
                "end": o_event["end"]["dateTime"],
                "extendedProps": {"originatingSource": "Fra Outlook kalender"},
            },
            [
                outlook_event
                for outlook_event in outlook_events
                if outlook_event["isCancelled"] == False
            ],
        )
    )

    return events
