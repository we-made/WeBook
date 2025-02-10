from django.apps import AppConfig


class CeleryHaystackConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webook.celery_haystack"

    def ready(self):
        import webook.celery_haystack.systask

        return super().ready()
