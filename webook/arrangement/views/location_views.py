
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
from webook.utils.meta.meta_view_mixins import MetaMixin, GenericListTemplateMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Locations"),
        section_icon="fas fa-building",
        section_crumb_url=reverse("arrangement:location_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:location_detail",
            create_url="arrangement:location_create",
            edit_url="arrangement:location_edit",
            delete_url="arrangement:location_delete",
            list_url="arrangement:location_list",
        )
    )


class LocationSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()