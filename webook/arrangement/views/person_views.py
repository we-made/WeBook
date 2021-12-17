from typing import Any, Dict, List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
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
from django.views.generic.base import View
from django.views.generic.edit import DeleteView
from webook.utils.meta_utils.section_manifest import SectionManifest
from webook.arrangement.models import Organization, Person
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


section_manifest = SectionManifest(
    section_title=_("People"),
    section_icon="fas fa-users",
    section_crumb_url=lambda: reverse("arrangement:location_list"),
    crudl_map=SectionCrudlPathMap(
        detail_url="arrangement:person_detail",
        create_url="arrangement:person_create",
        edit_url="arrangement:person_edit",
        delete_url="arrangement:person_delete",
        list_url="arrangement:person_list",
    )
)


class PersonListView(LoginRequiredMixin, CrumbMixin, GenericListTemplateMixin, ListView):
    queryset = Person.objects.all()
    template_name = "arrangement/list_view.html"
    section = section_manifest
    model = Person
    view_meta = ViewMeta.Preset.table(Person)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

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
    view_meta = ViewMeta.Preset.edit(Person)

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
    view_meta = ViewMeta.Preset.create(Person)

    def get_success_url(self) -> str:
        success_url = super().get_success_url()
        organization = self.request.POST.get("organization")
        created_user = self.object
        created_user.organizations.add(organization)
        created_user.save()
        return success_url


person_create_view = PersonCreateView.as_view()


class PersonDetailView(LoginRequiredMixin, DetailView):
    model = Person
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "arrangement/person/person_detail.html"
    view_meta = ViewMeta.Preset.detail(Person)

person_detail_view = PersonDetailView.as_view()


class PersonDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = Person
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name="arrangement/delete_view.html"
    view_meta = ViewMeta.Preset.delete(Person)

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:person_list"
        )

    section = section_manifest
    
person_delete_view = PersonDeleteView.as_view()


class OrganizationPersonMemberListView (LoginRequiredMixin, ListView):
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