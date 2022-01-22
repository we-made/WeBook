import json
from re import search
from typing import Any, Dict, List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
)
from django.core import serializers
from django.views.generic.base import View
from django.views.generic.edit import DeleteView
from webook.arrangement.views.organization_views import OrganizationSectionManifestMixin
from webook.utils.meta_utils.section_manifest import SectionManifest
from webook.arrangement.models import Organization, Person
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap
from django.db.models.functions import Concat
from django.db.models import Q, F


def get_section_manifest():
    return SectionManifest(
        section_title=_("People"),
        section_icon="fas fa-users",
        section_crumb_url=reverse("arrangement:location_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:person_detail",
            create_url="arrangement:person_create",
            edit_url="arrangement:person_edit",
            delete_url="arrangement:person_delete",
            list_url="arrangement:person_list",
        )
    )


class PersonSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class PersonListView(LoginRequiredMixin, PersonSectionManifestMixin, MetaMixin, GenericListTemplateMixin, ListView):
    queryset = Person.objects.all()
    template_name = "arrangement/list_view.html"
    model = Person
    view_meta = ViewMeta.Preset.table(Person)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

person_list_view = PersonListView.as_view()


class PersonUpdateView(LoginRequiredMixin, PersonSectionManifestMixin, MetaMixin, UpdateView):
    model = Person
    fields = [
        "personal_email",
        "first_name",
        "middle_name",
        "last_name",
        "birth_date",        
    ]
    template_name = "arrangement/person/person_form.html"
    view_meta = ViewMeta.Preset.edit(Person)

person_update_view = PersonUpdateView.as_view()


class PersonCreateView(LoginRequiredMixin, PersonSectionManifestMixin, MetaMixin, CreateView):
    model = Person
    fields = [
        "personal_email",
        "first_name",   
        "middle_name",
        "last_name",
        "birth_date",        
    ]
    template_name = "arrangement/person/person_form.html"
    view_meta = ViewMeta.Preset.create(Person)

    def get_success_url(self) -> str:
        success_url = super().get_success_url()
        organization = self.request.POST.get("organization")
        created_user = self.object
        created_user.organizations.add(organization)
        created_user.save()
        return success_url

person_create_view = PersonCreateView.as_view()


class PersonDetailView(LoginRequiredMixin, PersonSectionManifestMixin, MetaMixin, DetailView):
    model = Person
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/person/person_detail.html"
    view_meta = ViewMeta.Preset.detail(Person)

person_detail_view = PersonDetailView.as_view()


class PersonDeleteView(LoginRequiredMixin, PersonSectionManifestMixin, MetaMixin, DeleteView):
    model = Person
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name="arrangement/delete_view.html"
    view_meta = ViewMeta.Preset.delete(Person)

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:person_list"
        )
    
person_delete_view = PersonDeleteView.as_view()


class OrganizationPersonMemberListView (LoginRequiredMixin, OrganizationSectionManifestMixin, MetaMixin, ListView):
    model = Person
    template_name = "arrangement/person/partials/_organization_member_list.html"
    view_meta = ViewMeta.Preset.table(Person)

    def get_queryset(self):
        organization = self.request.GET.get('organization')
        return Organization.objects.filter(
            id=organization
        ).first().members

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["organization"] = self.request.GET.get('organization')
        return context

organization_person_member_list_view = OrganizationPersonMemberListView.as_view()


class SearchPeopleAjax (LoginRequiredMixin, ListView):

    def post(self, request):
        body_data = json.loads(request.body.decode('utf-8'))
        search_term = body_data["term"]

        # This avoids concatenation issues. Working with the full name may be difficult, should middle_name be unspecified
        # One could for instance end up with a string like this in the comparison: "John  Smith" as opposed to the intended "John Smith"
        # The best solution seems to be to just remove spaces from the user input, and the concatenation, and the issue is eliminated.
        search_term.replace(' ', "") 

        people = []
        if (search_term == ""):
            people = Person.objects.all()
        else:
            people = Person.objects\
                .annotate(afull_name=Concat('first_name', 'middle_name', 'last_name'))\
                .filter(afull_name__contains=search_term)

        response = serializers.serialize("json", people)

        return JsonResponse(response, safe=False)
        

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        people = Person.objects.filter(full_name__unaccent__icontains(request.GET["term"]))
        response = serializers.serialize("json", people)
        return JsonResponse(response, safe=False)

search_people_ajax_view = SearchPeopleAjax.as_view()