"""refresh_buffers.py

This module contains the refresh_buffers command. This command is used to force a refresh of all buffers in the application.
Useful when changes have been made to how buffers are created, and want to also update retroactively.
"""

from django.core.management.base import BaseCommand

from webook.arrangement.models import Event


class Command(BaseCommand):
    help = "Refreshes all buffers in the application"

    def handle(self, *args, **options):
        all_events = Event.objects.all()
        for event in all_events:
            self.stdout.write(f"Refreshing buffer for event {event}")
            event.refresh_buffers()

        self.stdout.write(self.style.SUCCESS("Successfully refreshed all buffers"))
