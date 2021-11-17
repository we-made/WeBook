from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
)
from webook.utils.calendar_buddy import calendar_buddy
from datetime import datetime

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    #model = User
    model = User

    # These Next Two Lines Tell the View to Index
    #   Lookups by Username
    slug_field = "username"
    slug_url_kwarg = "username"

events = list()
event_1 = dict()
event_1["id"] = 1
event_1["title"] = "AAA EEEEE"
event_1["start"] = datetime.now()
event_1["end"] = datetime.now()
events.append(event_1)

calendar_context = calendar_buddy.new_calendar(
    events=events,
    resources=list(),
    context_type=calendar_buddy.CalendarContext.FULLCALENDAR
).configure_ui(
    view = 0,
    views = ["timeGridWeek"],
    locale = "nbLocale",
    weekNumbers = True,
    nowIndicator = True,
    allDaySlot = False
)

user_detail_view = UserDetailView.as_view(extra_context={'calendar_context': calendar_context})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = [
        "name",
    ]

    # We already imported user in the View code above,
    #   remember?
    model = User

    # Send the User Back to Their Own Page after a
    #   successful Update
    def get_success_url(self):
        return reverse(
            "users:detail",
            kwargs={'username': self.request.user.username},
        )

    def get_object(self):
        # Only Get the User Record for the
        #   User Making the Request
        return User.objects.get(
            username=self.request.user.username
        )


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse(
            "users:detail",
            kwargs={"username": self.request.user.username},
        )


user_redirect_view = UserRedirectView.as_view()
