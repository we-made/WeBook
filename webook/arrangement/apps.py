from django.apps import AppConfig
from django.db import connection


class ArrangementConfig(AppConfig):
    name = "webook.arrangement"

    def ready(self):
        import webook.arrangement.signals
        import webook.arrangement.systask

        super().ready()
