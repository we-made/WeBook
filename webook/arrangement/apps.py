from django.apps import AppConfig


class ArrangementConfig(AppConfig):
    name = 'webook.arrangement'

    def ready(self):
        import webook.arrangement.signals
