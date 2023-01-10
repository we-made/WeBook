import os
from datetime import date, datetime, timedelta
from typing import List

import pytz
from django.core.management.base import BaseCommand, CommandError, CommandParser

from webook.arrangement.models import Arrangement, Event, Note


class Command(BaseCommand):
    help = "Sanitize notes containing PII after a set amount of time after end of arrangement"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("delete_after_n_days", type=int)

    def handle(self, *args, **options):
        arrangements: List[Arrangement] = Arrangement.objects.all()

        for arrangement in arrangements:
            latest_activity: datetime = arrangement.event_set.order_by("end").first()
            if latest_activity is None:
                continue

            latest_end = latest_activity.end

            tz = pytz.timezone("Europe/Oslo")

            is_ready_for_deletion = (
                tz.localize(datetime.now()) - latest_end
            ).days >= options["delete_after_n_days"]

            if not is_ready_for_deletion:
                continue

            notes: List[Note] = list(arrangement.notes.all())

            event: Event
            for event in arrangement.event_set.all():
                notes += list(event.notes.all())

            if len(notes) == 0:
                continue

            for note in filter(lambda x: x.has_personal_information, notes):
                note.content = "** Notat sanitisert etter endt arrangement grunnet personlig identifiserende informasjon **"
                note.save()
