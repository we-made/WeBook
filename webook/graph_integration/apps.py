from django.apps import AppConfig


class GraphIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webook.graph_integration"

    def ready(self):
        from . import signals
