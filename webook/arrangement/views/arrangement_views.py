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
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.meta_utils.section_manifest import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Arrangements"),
        section_icon="fas fa-clock",
        section_crumb_url=reverse("arrangement:arrangement_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:arrangement_detail",
            create_url="arrangement:arrangement_create",
            edit_url="arrangement:arrangement_edit",
            delete_url="arrangement:arrangement_delete",
            list_url="arrangement:arrangement_list",
        )
    )


class ArrangementSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class ArrangementDetailView (LoginRequiredMixin, ArrangementSectionManifestMixin, MetaMixin, DetailView):
    model = Arrangement
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(Arrangement)
    template_name = "arrangement/arrangement/arrangement_detail.html"

arrangement_detail_view = ArrangementDetailView.as_view()


class ArrangementListView(LoginRequiredMixin, ArrangementSectionManifestMixin, GenericListTemplateMixin, MetaMixin, ListView):
    queryset = Arrangement.objects.all()
    template_name = "arrangement/list_view.html"
    model = Arrangement
    view_meta = ViewMeta.Preset.table(Arrangement)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

arrangement_list_view = ArrangementListView.as_view()


class ArrangementCreateView (LoginRequiredMixin, ArrangementSectionManifestMixin, MetaMixin, CreateView):
    model = Arrangement
    fields = [
        "name",
        "audience",
        "starts",
        "ends",
        "responsible",
    ]
    template_name = "arrangement/arrangement/arrangement_form.html"
    view_meta = ViewMeta.Preset.create(Arrangement)

arrangement_create_view = ArrangementCreateView.as_view()


class ArrangementUpdateView(LoginRequiredMixin, ArrangementSectionManifestMixin, MetaMixin, UpdateView):
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
    view_meta = ViewMeta.Preset.edit(Arrangement)

arrangement_update_view = ArrangementUpdateView.as_view()


class ArrangementDeleteView(LoginRequiredMixin, ArrangementSectionManifestMixin, MetaMixin, DeleteView):
    model = Arrangement
    current_crumb_title = _("Delete Arrangement")
    section_subtitle = _("Edit Arrangement")
    template_name = "arrangement/delete_view.html"
    view_meta = ViewMeta.Preset.delete(Arrangement)

arrangement_delete_view = ArrangementDeleteView.as_view()
