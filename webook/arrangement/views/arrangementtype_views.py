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
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView
from webook.arrangement.forms.arrangement_type_forms import CreateArrangementTypeForm, UpdateArrangementTypeForm
from webook.arrangement.models import Arrangement, ArrangementType
from webook.arrangement.views.generic_views.archive_view import ArchiveView
from webook.arrangement.views.mixins.multi_redirect_mixin import MultiRedirectMixin
from webook.arrangement.views.generic_views.search_view import SearchView
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.crumbinator.crumb_node import CrumbNode
from django.views.generic.edit import ModelFormMixin
from webook.utils import crumbs
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin, GenericTreeListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Arrangement Type"),
        section_icon="fas fa-suitcase",
        section_crumb_url=reverse("arrangement:arrangement_type_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url=None,
            create_url="arrangement:arrangement_type_create",
            edit_url="arrangement:arrangement_type_edit",
            delete_url="arrangement:arrangement_type_delete",
            list_url="arrangement:arrangement_type_list",
        )
    )


class ArrangementTypeSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class ArrangementTypeListView(LoginRequiredMixin, ArrangementTypeSectionManifestMixin, GenericTreeListTemplateMixin, MetaMixin, ListView):
    template_name = "arrangement/tree_list_view.html"
    model = ArrangementType
    queryset = ArrangementType.objects.all()
    view_meta = ViewMeta.Preset.table(ArrangementType)
    fields = [
        "name_en"
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

arrangement_type_list_view = ArrangementTypeListView.as_view()


class ArrangementTypeDetailView(LoginRequiredMixin, ArrangementTypeSectionManifestMixin, MetaMixin, DetailView):
    model = ArrangementType
    slug_field="slug"
    slug_url_kwarg="slug"
    view_meta = ViewMeta.Preset.detail(ArrangementType)
    template_name = "arrangement/arrangementtype/arrangement_type_detail.html"

arrangement_type_detail_view = ArrangementTypeDetailView.as_view()


class ArrangementTypeCreateView(LoginRequiredMixin, ArrangementTypeSectionManifestMixin, MetaMixin, MultiRedirectMixin, CreateView, ModelFormMixin):
    form_class = CreateArrangementTypeForm
    model = ArrangementType
    template_name = "arrangement/arrangementtype/arrangement_type_form.html"
    view_meta = ViewMeta.Preset.create(ArrangementType)

    success_urls_and_messages = {
        "submitAndNew": {
            "url": reverse_lazy( "arrangement:arrangement_type_create"),
            "msg": _("Successfully created arrangement type")
        },
        "submit": {
            "url": reverse_lazy("arrangement:arrangement_type_list"),
        }
    }

arrangement_type_create_view = ArrangementTypeCreateView.as_view()


class ArrangementTypeUpdateView(LoginRequiredMixin, ArrangementTypeSectionManifestMixin, MetaMixin, UpdateView, ModelFormMixin):
    form_class = UpdateArrangementTypeForm
    model = ArrangementType
    view_meta = ViewMeta.Preset.edit(ArrangementType)
    template_name = "arrangement/arrangementtype/arrangement_type_form.html"

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:arrangement_type_list"
        )

arrangement_type_update_view = ArrangementTypeUpdateView.as_view()


class ArrangementTypeDeleteView(LoginRequiredMixin, ArrangementTypeSectionManifestMixin, MetaMixin, ArchiveView):
    model = ArrangementType
    view_meta = ViewMeta.Preset.delete(ArrangementType)
    template_name = "arrangement/delete_view.html"

    def get_success_url(self) -> str:
        return reverse(
            "arrangement:arrangement_type_list"
        )

arrangement_type_delete_view = ArrangementTypeDeleteView.as_view()
