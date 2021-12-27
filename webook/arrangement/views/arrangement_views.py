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