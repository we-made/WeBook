import json
from ast import Delete
from pipes import Template

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView

from webook.arrangement.forms.note_forms import CreateNoteForm, UpdateNoteForm
from webook.arrangement.models import Event, Location, Note
from webook.arrangement.views.generic_views.archive_view import JsonArchiveView
from webook.arrangement.views.generic_views.json_form_view import JsonFormView
from webook.authorization_mixins import PlannerAuthorizationMixin
from webook.utils.meta_utils import SectionCrudlPathMap, SectionManifest, ViewMeta
from webook.utils.meta_utils.meta_mixin import MetaMixin
from webook.utils.meta_utils.typeToModels import getEntityTypeToModelsDict


class NotesOnEntityView(LoginRequiredMixin, PlannerAuthorizationMixin, TemplateView):
    model = Note
    template_name = "arrangement/notes/notes_on_entity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ENTITY_PK"] = self.request.GET.get("entityPk")
        context["ENTITY_TYPE"] = self.request.GET.get("entityType")
        return context


notes_on_entity_view = NotesOnEntityView.as_view()


class GetNotesForEntityView(LoginRequiredMixin, PlannerAuthorizationMixin, ListView):
    model = Note
    template_name = "arrangement/notes/notes_on_entity.html"

    def get_queryset(self):
        entity_type = self.request.GET.get("entityType")
        entity_pk = self.request.GET.get("entityPk")

        model_instance = (
            getEntityTypeToModelsDict()[entity_type]
            .objects.filter(pk=entity_pk)
            .first()
        )

        return model_instance.notes.select_related("author").all()

    def get(self, request, *args, **kwargs):
        notes = []
        for note in self.get_queryset():
            notes.append(
                {
                    "author": note.author.full_name,
                    "content": note.content,
                    "pk": note.pk,
                    "created": note.created,
                }
            )
        return JsonResponse(json.dumps(notes, cls=DjangoJSONEncoder), safe=False)


get_notes_view = GetNotesForEntityView.as_view()


class CreateNoteView(
    LoginRequiredMixin, PlannerAuthorizationMixin, CreateView, JsonFormView
):
    form_class = CreateNoteForm

    def form_valid(self, form):
        form.save(self.request.user.person)
        return super().form_valid(form)


create_note_view = CreateNoteView.as_view()


class UpdateNoteView(
    LoginRequiredMixin, PlannerAuthorizationMixin, UpdateView, JsonFormView
):
    model = Note
    form_class = UpdateNoteForm
    pk_url_kwarg = "entityPk"

    def form_valid(self, form):
        form.save(self.request.user.person)
        return super().form_valid(form)


update_note_view = UpdateNoteView.as_view()


class DeleteNoteView(LoginRequiredMixin, PlannerAuthorizationMixin, JsonArchiveView):
    pk_url_kwarg = "entityPk"
    model = Note


delete_note_view = DeleteNoteView.as_view()
