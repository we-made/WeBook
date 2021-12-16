from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse
from django.urls import reverse
from webook.arrangement.models import Person
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    FormView,
)

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These Next Two Lines Tell the View to Index
    #   Lookups by Username
    slug_field = "slug"
    slug_url_kwarg = "slug"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = [
        "first_name",
        "middle_name",
        "last_name",
        "birth_date",
    ]
    template_name = "users/user_form.html"
    model = Person
    # Send the User Back to Their Own Page after a
    #   successful Update
    def get_success_url(self):
        return reverse(
            "users:detail",
            kwargs={'slug': self.request.user.slug},
        )

    def get_object(self):
        # Only Get the User Record for the
        #   User Making the Request
        person_object = Person()
        user = User.objects.get(
            slug=self.request.user.slug
        )
        if user is not None:
            if (user.person is not None):
                person_object = user.person
            else:
                # In some specific cases it is possible to create an user without a person.
                # In those cases, if one was to save name changes and so on, the person would be saved without the user entity referencing it.
                # This takes care of that edge-case. Albeit it would be best to make sure that a person is always associated with the user.
                # The sharp edge of this solution is that if the user chooses to abort the update process, we will have an empty person.
                # That isn't the end of the world - and it will be resolved by the user simply updating at a later date.
                person_object = Person()
                person_object.save()
                user.person = person_object
                user.save()
        return person_object

user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse(
            "users:detail",
            kwargs={"slug": self.request.user.slug},
        )


user_redirect_view = UserRedirectView.as_view()
