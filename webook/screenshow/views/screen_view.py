from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views.generic.edit import DeleteView

from webook.arrangement.views.generic_views.json_list_view import JsonListView
from webook.screenshow.models import ScreenResource
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta_utils.meta_mixin import MetaMixin


def get_section_manifest():
    return SectionManifest(
        section_title=_("Screen Resource"),
        section_icon="fas fa-television",
        section_crumb_url=reverse("screenshow:screen_list"),
        crudl_map=SectionCrudlPathMap(
            list_url="screenshow:screen_list",
            detail_url=None,
            create_url="screenshow:screen_create",
            edit_url="screenshow:screen_edit",
            delete_url="screenshow:screen_delete",
        ),
    )


class ScreenSectionManifestMixin(UserPassesTestMixin):
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()

    def _is_member(self):
        return (
            self.request.user.groups.filter(name="display_organizer").exists()
            or self.request.user.is_superuser
        )

    def test_func(self):
        return self._is_member()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ScreenListView(
    LoginRequiredMixin,
    ScreenSectionManifestMixin,
    MetaMixin,
    GenericListTemplateMixin,
    ListView,
):
    queryset = ScreenResource.objects.all()
    fields = ["items_shown", "room"]
    template_name = "common/list_view.html"
    model = ScreenResource
    view_meta = ViewMeta.Preset.table(ScreenResource)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context


screen_list_view = ScreenListView.as_view()


class ScreenCreateView(
    LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, CreateView
):
    model = ScreenResource
    fields = [
        "screen_model",
        "folder_path",
        "items_shown",
        "room",
        "generated_name",
    ]
    template_name = "screenshow/screen/screen_form.html"
    view_meta = ViewMeta.Preset.create(ScreenResource)

    def get_success_url(self) -> str:
        return reverse("screenshow:screen_list")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(">> Form Invalid")
        print(form.errors)
        print(form)
        return super().form_invalid(form)


screen_create_view = ScreenCreateView.as_view()


class ScreenUpdateView(ScreenCreateView, UpdateView):
    view_meta = ViewMeta.Preset.edit(ScreenResource)


screen_update_view = ScreenUpdateView.as_view()


class ScreenDetailView(
    LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, DetailView
):
    model = ScreenResource
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "screenshow/screen/screen_detail.html"
    view_meta = ViewMeta.Preset.detail(ScreenResource)


screen_detail_view = ScreenDetailView.as_view()


class ScreenDeleteView(
    LoginRequiredMixin, ScreenSectionManifestMixin, MetaMixin, DeleteView
):
    model = ScreenResource
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "common/delete_view.html"
    view_meta = ViewMeta.Preset.delete(ScreenResource)

    def get_success_url(self) -> str:
        return reverse("screenshow:screen_list")


screen_delete_view = ScreenDeleteView.as_view()
