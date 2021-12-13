from typing import List
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    RedirectView,
    UpdateView,
    ListView,
    CreateView,
    TemplateView
)
from django.views.generic.edit import DeleteView
from webook.arrangement.models import Arrangement
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.utils.crudl_utils.path_maps import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin


section_manifest  = {
    "SECTION_TITLE": _("Arrangements"),
    "SECTION_ICON": "fas fa-clock",
    "SECTION_CRUMB_URL": lambda: reverse("arrangement:arrangement_list"),
    "CRUDL_MAP": SectionCrudlPathMap(
        detail_url="arrangement:arrangement_detail",
        create_url="arrangement:arrangement_create",
        edit_url="arrangement:arrangement_edit",
        delete_url="arrangement:arrangement_delete",
        list_url="arrangement:arrangement_list",
    )
}


class ArrangementDetailView (LoginRequiredMixin, CrumbMixin, DetailView):
    model = Arrangement

    slug_field = "slug"
    slug_url_kwarg = "slug"

    section = section_manifest
    entity_name_attribute = "name"

    template_name = "arrangement/arrangement/arrangement_detail.html"

arrangement_detail_view = ArrangementDetailView.as_view()


class ArrangementListView(LoginRequiredMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    queryset = Arrangement.objects.all()
    section = section_manifest
    template_name = "arrangement/list_view.html"
    model = Arrangement
    section_subtitle = _("All Arrangements")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section["CRUDL_MAP"]
        return context

arrangement_list_view = ArrangementListView.as_view()


class ArrangementCreateView (LoginRequiredMixin, CrumbMixin, CreateView):
    model = Arrangement
    fields = [
        "name",
        "audience",
        "starts",
        "ends",
        "responsible",
    ]
    current_crumb_title = _("Create Arrangement")
    section_subtitle = _("Create Arrangement")
    template_name = "arrangement/arrangement/arrangement_form.html"
    section = section_manifest

arrangement_create_view = ArrangementCreateView.as_view()


class ArrangementUpdateView(LoginRequiredMixin, CrumbMixin, UpdateView):
    model = Arrangement
    fields = [
        "name",
        "audience",
        "starts",
        "ends",
        "responsible",
    ]
    current_crumb_title = _("Edit Arrangement")
    section_subtitle = _("Edit Arrangement")
    template_name = "arrangement/arrangement/arrangement_form.html"
    section = section_manifest

arrangement_update_view = ArrangementUpdateView.as_view()


class ArrangementDeleteView(LoginRequiredMixin, CrumbMixin, DeleteView):
    model = Arrangement
    current_crumb_title = _("Delete Arrangement")
    section_subtitle = _("Edit Arrangement")
    template_name = "arrangement/delete_view.html"
    section = section_manifest

arrangement_delete_view = ArrangementDeleteView.as_view()
