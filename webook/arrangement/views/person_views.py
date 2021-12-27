
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
from webook.arrangement.models import Person
from django.views.generic.edit import DeleteView
from webook.utils.meta.meta_view_mixins import MetaMixin, GenericListTemplateMixin
from webook.utils.meta.meta_types import SectionManifest, ViewMeta, SectionCrudlPathMap


def get_section_manifest():
    return SectionManifest(
        section_title=_("People"),
        section_icon="fas fa-users",
        section_crumb_url=reverse("arrangement:location_list"),
        crudl_map=SectionCrudlPathMap(
            detail_url="arrangement:person_detail",
            create_url="arrangement:person_create",
            edit_url="arrangement:person_edit",
            delete_url="arrangement:person_delete",
            list_url="arrangement:person_list",
        )
    )


class PersonSectionManifestMixin:
    def __init__(self) -> None:
        super().__init__()
        self.section = get_section_manifest()


class PersonListView(LoginRequiredMixin, PersonSectionManifestMixin, MetaMixin, GenericListTemplateMixin, ListView):
    queryset = Person.objects.all()
    template_name = "arrangement/list_view.html"
    model = Person
    view_meta = ViewMeta.Preset.table(Person)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["CRUDL_MAP"] = self.section.crudl_map
        return context

person_list_view = PersonListView.as_view()
