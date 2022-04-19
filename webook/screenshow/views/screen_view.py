from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    UpdateView,
    ListView,
    CreateView,
)
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from webook.screenshow.models import ScreenResource
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Screen Resource"),
        section_icon="fas fa-television",
        section_crumb_url=reverse("screenshow:screen_list"),
        crudl_map=SectionCrudlPathMap(
            list_url="screenshow:screen_list",
            detail_url="screenshow:screen_detail",
            create_url="screenshow:screen_create",
            edit_url="screenshow:screen_edit",
            delete_url="screenshow:screen_delete",
        )
    )


class ScreenSectionManifestMixin(UserPassesTestMixin):
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()

    def _is_member(self):
        return self.request.user.groups.filter(name='display_organizer').exists() or self.request.user.is_superuser

    def test_func(self):
        return self._is_member()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ScreenListView(LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, GenericListTemplateMixin, ListView):
    queryset = ScreenResource.objects.all()
    template_name = "screenshow/list_view.html"
    model = ScreenResource
    view_meta = ViewMeta.Preset.table(ScreenResource)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context


screen_list_view = ScreenListView.as_view()


class ScreenCreateView(LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, CreateView):
    model = ScreenResource
    fields = [
        "name",
        "name_en",
        "quantity",
        "is_room_screen",
    ]
    template_name = "screenshow/screen/screen_form.html"
    view_meta = ViewMeta.Preset.create(ScreenResource)


screen_create_view = ScreenCreateView.as_view()


class ScreenUpdateView(LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, UpdateView):
    model = ScreenResource
    fields = [
        "name",
        "name_en",
        "quantity",
        "is_room_screen",
    ]
    template_name = "screenshow/screen/screen_form.html"
    view_meta = ViewMeta.Preset.create(ScreenResource)


screen_update_view = ScreenUpdateView.as_view()


class ScreenDetailView(LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, DetailView):
    model = ScreenResource
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "screenshow/screen/screen_detail.html"
    view_meta = ViewMeta.Preset.detail(ScreenResource)


screen_detail_view = ScreenDetailView.as_view()


class ScreenDeleteView(LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, DeleteView):
    model = ScreenResource
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "screenshow/delete_view.html"
    view_meta = ViewMeta.Preset.delete(ScreenResource)

    def get_success_url(self) -> str:
        return reverse(
            "screenshow:screen_list"
        )

screen_delete_view = ScreenDeleteView.as_view()

