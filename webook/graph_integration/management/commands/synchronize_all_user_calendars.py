import os

from django.core.management.base import BaseCommand, CommandParser
from ...tasks import synchronize_all_user_calendars


class Command(BaseCommand):
    help = "Synchronize all user calendars"

    def handle(self, *args, **options):
        print("Synchronizing all user calendars")
        synchronize_all_user_calendars()
        print("Tasks have been registered with Celery")
