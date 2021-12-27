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
from webook.arrangement.models import Organization
from django.views.generic.edit import DeleteView
from webook.utils.meta.meta_view_mixins import MetaMixin, GenericListTemplateMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Organizations"),
        section_icon="fas fa-dollar-sign",
        section_crumb_url=reverse("arrangement:organization_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:organization_detail",
            create_url="arrangement:organization_create",
            edit_url="arrangement:organization_edit",
            delete_url="arrangement:organization_delete",
            list_url="arrangement:organization_list",
        )
    )


class OrganizationSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()
