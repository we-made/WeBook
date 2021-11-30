from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
)
from webook.arrangement.models import Person


class PersonListView(LoginRequiredMixin, ListView):
    queryset = Person.objects.all()
    template_name = "arrangement/person/person_list.html"

person_list_view = PersonListView.as_view()


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    fields = [
        "personal_email",
        "first_name",
        "middle_name",
        "last_name",
        "birth_date",        
    ]
    template_name = "arrangement/person/person_form.html"

person_update_view = PersonUpdateView.as_view()


class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    fields = [
        "personal_email",
        "first_name",
        "middle_name",
        "last_name",
        "birth_date",        
    ]
    template_name = "arrangement/person/person_form.html"

person_create_view = PersonCreateView.as_view()


class PersonDetailView(LoginRequiredMixin, DetailView):
    model = Person
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/person/person_detail.html"

person_detail_view = PersonDetailView.as_view()