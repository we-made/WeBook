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
from webook.arrangement.models import Arrangement, Audience
from webook.arrangement.views.custom_views.crumb_view import CrumbMixin
from webook.crumbinator.crumb_node import CrumbNode
from webook.utils import crumbs
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


class AudienceListView(LoginRequiredMixin, AudienceSectionManifestMixin, GenericListTemplateMixin, CrumbMixin, ListView):
    template_name = "arrangement/list_view.html"
    model = Audience
    queryset = Audience.objects.all()
    view_meta = ViewMeta.Preset.table(Audience)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        root_node = crumbs.get_root_crumb(self.request.user.slug)
        section_node = CrumbNode(
			title=self.section.section_title,
			url=reverse(self.section.crudl_map.list_url) if self.section.crudl_map is not None else "",
            parent=root_node,
            icon_class="fas fa-users"
		)
        current_node=CrumbNode(
            title=self.view_meta.subtitle,
            url="",
            html_classes="active",
            parent=section_node,
            icon_class="fas fa-list"
        )

        context["CRUMBS"] = root_node
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

audience_list_view = AudienceListView.as_view()


class AudienceDetailView(LoginRequiredMixin, AudienceSectionManifestMixin, CrumbMixin, DetailView):
    model = Audience
    slug_field = "slug"
    slug_url_kwarg = "slug"
    view_meta = ViewMeta.Preset.detail(Audience)
    template_name = "arrangement/audience/audience_detail.html"

audience_detail_view = AudienceDetailView.as_view()


class AudienceCreateView(LoginRequiredMixin, AudienceSectionManifestMixin, CrumbMixin, CreateView):
    model = Audience
    fields = [
        "name"
    ]
    template_name = "arrangement/audience/audience_form.html"
    view_meta = ViewMeta.Preset.create(Audience)

audience_create_view = AudienceCreateView.as_view()


class AudienceUpdateView(LoginRequiredMixin, AudienceSectionManifestMixin, CrumbMixin, UpdateView):
    model = Audience
    fields = [
        "name"
    ]
    view_meta = ViewMeta.Preset.edit(Audience)
    template_name = "arrangement/audience/audience_form.html"

audience_update_view = AudienceUpdateView.as_view()


class AudienceDeleteView(LoginRequiredMixin, AudienceSectionManifestMixin, CrumbMixin, DeleteView):
    model = Audience
    view_meta = ViewMeta.Preset.delete(Audience)
    template_name = "arrangement/delete_view.html"

audience_delete_view = AudienceDeleteView.as_view()
