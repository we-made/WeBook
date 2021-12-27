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
from webook.arrangement.models import OrganizationType
from django.views.generic.edit import DeleteView
from webook.utils.meta.meta_view_mixins import MetaMixin, GenericListTemplateMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Organization Types"),
        section_icon="fas fa-object-group",
        section_crumb_url=reverse("arrangement:organizationtype_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:organizationtype_detail",
            create_url="arrangement:organizationtype_create",
            edit_url="arrangement:organizationtype_edit",
            delete_url="arrangement:organizationtype_delete",
            list_url="arrangement:organizationtype_list",
        )
    )


class OrganizationTypeSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()