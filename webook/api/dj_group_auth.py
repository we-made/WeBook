from typing import Any, Optional
from django.http import HttpRequest
from ninja.security.apikey import APIKeyCookie
from django.contrib.auth.models import Group


class SessionGroupAuth(APIKeyCookie):
    def __init__(self, group_name: str):
        self.group_name = group_name
        self.param_name = f"{group_name}_session"

        if not self.group_name:
            raise ValueError("group_name must be provided")

        if not Group.objects.filter(name=self.group_name).exists():
            raise ValueError(f"Group {self.group_name} does not exist")

        super().__init__()

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if request.user.is_authenticated and (
            request.user.groups.filter(name=self.group_name).exists()
            or request.user.is_superuser
        ):
            return request.user

        return None
