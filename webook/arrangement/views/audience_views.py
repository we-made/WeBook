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
from webook.arrangement.models import Audience
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.meta_utils.section_manifest import SectionCrudlPathMap
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Audience"),
        section_icon="fas fa-user",
        section_crumb_url=reverse("arrangement:audience_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:audience_detail",
            create_url="arrangement:audience_create",
            edit_url="arrangement:audience_edit",
            delete_url="arrangement:audience_delete",
            list_url="arrangement:audience_list",
        )
    )


class AudienceSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class AudienceListView(LoginRequiredMixin, AudienceSectionManifestMixin, GenericListTemplateMixin, MetaMixin, ListView):
    template_name = "arrangement/list_view.html"
    model = Audience
    queryset = Audience.objects.all()
    view_meta = ViewMeta.Preset.table(Audience)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

audience_list_view = AudienceListView.as_view()


class AudienceDetailView(LoginRequiredMixin, AudienceSectionManifestMixin, MetaMixin, DetailView):
    model = Audience
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(Audience)
    template_name = "arrangement/audience/audience_detail.html"

audience_detail_view = AudienceDetailView.as_view()


class AudienceCreateView(LoginRequiredMixin, AudienceSectionManifestMixin, MetaMixin, CreateView):
    model = Audience
    fields = [
        "name"
    ]
    template_name = "arrangement/audience/audience_form.html"
    view_meta = ViewMeta.Preset.create(Audience)

audience_create_view = AudienceCreateView.as_view()