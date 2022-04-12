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
from webook.screenshow.models import DisplayLayout, ScreenResource, ScreenGroup
from webook.screenshow.forms import DisplayLayoutForm
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin
from webook.utils.meta_utils import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("Display Layout"),
        section_icon="fas fa-television",
        section_crumb_url=reverse("screenshow:layout_list"),
        crudl_map=SectionCrudlPathMap(
            list_url="screenshow:layout_list",
            detail_url="screenshow:layout_detail",
            create_url="screenshow:layout_create",
            edit_url="screenshow:layout_edit",
            delete_url="screenshow:layout_delete",
        )
    )


class LayoutSectionManifestMixin(UserPassesTestMixin):
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()

    def _is_member(self):
        return self.request.user.groups.filter(name='display_organizer').exists()

    def test_func(self):
        return self._is_member()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_display_organizer"] = self._is_member()
        return context


class LayoutListView(LoginRequiredMixin, LayoutSectionManifestMixin, MetaMixin, GenericListTemplateMixin, ListView):
    queryset = DisplayLayout.objects.all()
    template_name = "screenshow/list_view.html"
    model = DisplayLayout
    view_meta = ViewMeta.Preset.table(DisplayLayout)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context


layout_list_view = LayoutListView.as_view()


class LayoutCreateView(LoginRequiredMixin, LayoutSectionManifestMixin, MetaMixin, CreateView):
    model = DisplayLayout
    form_class = DisplayLayoutForm
    template_name = "screenshow/layout/layout_form.html"
    view_meta = ViewMeta.Preset.create(DisplayLayout)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['screen_list'] = ScreenResource.objects.order_by('name')
        context['group_list'] = ScreenGroup.objects.order_by('group_name')
        return context


layout_create_view = LayoutCreateView.as_view()


class LayoutUpdateView(LoginRequiredMixin, LayoutSectionManifestMixin, MetaMixin, UpdateView):
    model = DisplayLayout
    form_class = DisplayLayoutForm
    template_name = "screenshow/layout/layout_form.html"
    view_meta = ViewMeta.Preset.create(DisplayLayout)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['screen_list'] = ScreenResource.objects.order_by('name')
        context['group_list'] = ScreenGroup.objects.order_by('group_name')
        return context


layout_update_view = LayoutUpdateView.as_view()


class LayoutDetailView(LoginRequiredMixin, LayoutSectionManifestMixin, MetaMixin, DetailView):
    model = DisplayLayout
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "screenshow/layout/layout_detail.html"
    view_meta = ViewMeta.Preset.detail(DisplayLayout)


layout_detail_view = LayoutDetailView.as_view()


class LayoutDeleteView(LoginRequiredMixin, LayoutSectionManifestMixin, MetaMixin, DeleteView):
    model = DisplayLayout
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "screenshow/delete_view.html"
    view_meta = ViewMeta.Preset.delete(DisplayLayout)

    def get_success_url(self) -> str:
        return reverse(
            "screenshow:layout_list"
        )

layout_delete_view = LayoutDeleteView.as_view()

