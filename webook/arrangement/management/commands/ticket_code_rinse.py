from typing import List
from django.core.management.base import BaseCommand
from webook.arrangement.models import Arrangement, PlanManifest, Event


class Command(BaseCommand):
    help = "Rinse 'undefined' from ticket code values"

    def handle(self, *args, **options):
        arrangements: List[Arrangement] = Arrangement.objects.all()
        manifests: List[PlanManifest] = PlanManifest.objects.all()
        events: List[Event] = Event.objects.all()

        for arrangement in arrangements:
            if arrangement.ticket_code == "undefined":
                print(f"Rinsing arrangement {arrangement.id}")
                arrangement.ticket_code = ""
                arrangement.save()
        for manifest in manifests:
            if manifest.ticket_code == "undefined":
                print(f"Rinsing manifest {manifest.id}")
                manifest.ticket_code = ""
                manifest.save()
        for event in events:
            if event.ticket_code == "undefined":
                print(f"Rinsing event {event.id}")
                event.ticket_code = ""
                event.save()

        print("Done rinsing")
