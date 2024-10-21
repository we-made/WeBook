from typing import Dict, List, Set, Tuple
import django
from django.apps import AppConfig
from django.urls import URLPattern
from django.utils.translation import gettext_lazy as _
import os
from django.db.migrations.recorder import MigrationRecorder


class ApiConfig(AppConfig):
    name = "webook.api"
    verbose_name = _("API")

    ignored_endpoints: Set[str] = {
        "api-root",
        "openapi-json",
        "openapi-view",
        "login_service_account",
    }

    def ready(self):
        pass
