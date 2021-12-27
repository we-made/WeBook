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
from webook.utils.meta.meta_view_mixins import MetaMixin
from webook.utils.meta.meta_types import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta.meta_view_mixins import GenericListTemplateMixin


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