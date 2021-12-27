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
from webook.utils.meta.meta_view_mixins import MetaMixin, GenericListTemplateMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Service Types"),
        section_icon="fas fa-concierge-bell",
        section_crumb_url=reverse("arrangement:servicetype_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:servicetype_detail",
            create_url="arrangement:servicetype_create",
            edit_url="arrangement:servicetype_edit",
            delete_url="arrangement:servicetype_delete",
            list_url="arrangement:servicetype_list",
        )
    )


class ServiceTypeSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()