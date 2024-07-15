from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApiConfig(AppConfig):
    name = "webook.api"
    verbose_name = _("API")

    def ready(self):
        pass  # Here.
