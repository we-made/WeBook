from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class BaseGroupsAuthorizationMixin(UserPassesTestMixin):
    group: str = None

    def _is_member_of_group(self):
        return (
            self.request.user.groups.filter(name=self.group).exists()
            or self.request.user.is_superuser
        )

    def test_func(self):
        return self._is_member_of_group()


class PlannerAuthorizationMixin(BaseGroupsAuthorizationMixin):
    """Require the user to be of the group planners or super user"""

    group = "planners"


class UserAdminAuthorizationMixin(BaseGroupsAuthorizationMixin):
    def _is_member_of_group(self) -> bool:
        return self.request.user.is_user_admin or self.request.user.is_superuser
