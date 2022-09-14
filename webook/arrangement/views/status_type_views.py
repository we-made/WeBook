from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, RedirectView, TemplateView, UpdateView
from django.views.generic.edit import DeleteView, ModelFormMixin

from webook.arrangement.forms.arrangement_type_forms import CreateArrangementTypeForm, UpdateArrangementTypeForm
from webook.arrangement.forms.status_type_forms import CreateStatusTypeForm, UpdateStatusTypeForm
from webook.arrangement.models import Arrangement, ArrangementType, StatusType
from webook.arrangement.views.generic_views.archive_view import ArchiveView
from webook.arrangement.views.generic_views.dialog_views import DialogView
from webook.arrangement.views.generic_views.jstree_list_view import JSTreeListView
from webook.arrangement.views.generic_views.search_view import SearchView
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin
from webook.arrangement.views.mixins.multi_redirect_mixin import MultiRedirectMixin
from webook.crumbinator.crumb_node import CrumbNode
from webook.utils import crumbs
from webook.utils.crudl_utils.view_mixins import GenericListTemplateMixin, GenericTreeListTemplateMixin
from webook.utils.meta_utils import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta_utils.meta_mixin import MetaMixin


def get_section_manifest():
    return SectionManifest(
        section_title=_("Status"),
        section_icon="fal fa-clipboard-check",
        section_crumb_url=None,#reverse("arrangement:arrangement_type_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url=None,
            create_url=None,#"arrangement:arrangement_type_create",
            edit_url=None,#"arrangement:arrangement_type_edit",
            delete_url=None,#"arrangement:arrangement_type_delete",
            list_url=None,#"arrangement:arrangement_type_list",
        )
    )


class StatusTypeSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context


class StatusTypeListView(LoginRequiredMixin, ListView, StatusTypeSectionManifestMixin):
    queryset = StatusType.objects.all()
    model = StatusType
    template = "arrangement/list_view.html"
    ViewMeta.Preset.table(StatusType)

status_type_list_view = StatusTypeListView.as_view()

class StatusTypeCreateView(LoginRequiredMixin, CreateView, StatusTypeSectionManifestMixin, DialogView):
    form_class = CreateStatusTypeForm
    model = StatusType
    template_name = "arrangement/statustype/statustype_form.html"
    view_meta = ViewMeta.Preset.create(StatusType)

    def get_success_url(self) -> str:
        return reverse("") # TODO: Redirect to list, or perhaps see how it is affected by dialog in arrtype?

status_type_create_view = StatusTypeCreateView.as_view()

class StatusTypeUpdateView(LoginRequiredMixin, UpdateView, StatusTypeSectionManifestMixin, DialogView):
    form_class = UpdateStatusTypeForm
    model = StatusType
    template_name = "arrangement/statustype/statustype_form.html"
    view_meta = ViewMeta.Preset.edit(StatusType)

status_type_update_view = StatusTypeUpdateView.as_view()
