from typing import List
from django.contrib.auth.models import Group


class AuthAgent:
    """
    Implements a simple authentication and authorization mechanism for Ninja API. Integrating with Django's
    authentication and authorization mechanisms.

    :param allowed_groups: List of groups that are allowed to access the API.
    :param authorize_hook: A callable that can be used to implement custom authorization logic.

    By default the authorization mechanism, without any groups or hooks, will allow only superusers access.
    To allow for other groups to access the API, the allowed_groups parameter should be set to a list of groups
    To implement custom authorization logic, the authorize_hook parameter should be set to a callable that takes
    a user object as an argument and returns a boolean value, indicating whether the user is authorized or not.

    In the future one should also add support for service accounts and JWT tokens.
    """

    def __init__(
        self,
        allowed_groups: List[Group] = None,
        authorize_hook: callable = None,
    ):
        self.allowed_groups = allowed_groups
        self.authorize_hook = authorize_hook

    def _is_authorized(self, user):
        if user.is_superuser:
            return True

        if self.authorize_hook:
            return self.authorize_hook(user)

        if self.allowed_groups:
            return user.groups.filter(
                pk__in=[group.pk for group in self.allowed_groups]
            ).exists()

        return False

    def authenticate(self, request):
        if request.user.is_authenticated and self._is_authorized(request.user):
            return request.user
        return None

    def __call__(self, request):
        return self.authenticate(request)
