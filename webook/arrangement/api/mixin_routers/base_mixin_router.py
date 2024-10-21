from django.http import Http404
from ninja import Router
from ninja.errors import HttpError

from webook.arrangement.models import Person


class BaseMixinRouter(Router):
    def _get_base_entity_or_404(self, parent_id: int):
        if self.model is None:
            raise NotImplementedError(
                "Model is not defined, MixinRouter should be inherited by a CrudRouter"
            )

        instance = self.model.objects.get(pk=parent_id)

        if instance is None:
            raise Http404("Parent entity not found")

        return instance

    def _get_user_person(self, request, raise_on_none=True) -> Person:
        """
        Get the person instance of the user

        :param request: The request object.
        :param raise_on_none: Whether to raise an error if the user does not have a person associated with it.

        :return: The person associated with the user triggering the request.

        :raises HttpError: If the user does not have a person associated with it and raise_on_none is True.
        """
        user = request.user

        if user.person is None and raise_on_none:
            raise HttpError(
                status_code=500,
                message="_get_user_person was called by a user without a person associated with it.",
            )

        return user.person
