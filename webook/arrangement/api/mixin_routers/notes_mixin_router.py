from typing import List, Optional
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import Router
from webook.api.schemas.base_schema import BaseSchema, ModelBaseSchema
from webook.arrangement.api.mixin_routers.base_mixin_router import BaseMixinRouter
from webook.arrangement.api.routers.person_router import PersonGetSchema
from webook.arrangement.api.schemas.notes import NoteCreateSchema, NoteGetSchema
from webook.arrangement.models import Note
from datetime import datetime


class NotesMixinRouter(BaseMixinRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_api_operation(
            operation_id="get_note_for_" + self.model_name_singular.lower(),
            description="Get a note for the " + self.model_name_singular,
            summary="Get a note for the " + self.model_name_singular,
            path="/notes/get",
            methods=["GET"],
            view_func=self.NoteFunctionality.get_retrieve_note_func(instance=self),
            response=NoteGetSchema,
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            operation_id="delete_note_from_" + self.model_name_singular.lower(),
            description="Delete a note from the " + self.model_name_singular,
            summary="Delete a note from the " + self.model_name_singular,
            path="/notes/delete",
            methods=["DELETE"],
            view_func=self.NoteFunctionality.get_delete_func(instance=self),
            response=NoteGetSchema,
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            operation_id="update_note_in_" + self.model_name_singular.lower(),
            description="Update a note in the " + self.model_name_singular,
            summary="Update a note in the " + self.model_name_singular,
            path="/notes/put",
            methods=["PUT"],
            view_func=self.NoteFunctionality.get_put_func(instance=self),
            response=NoteCreateSchema,
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            operation_id="list_notes_of_" + self.model_name_singular.lower(),
            description="List all notes in the " + self.model_name_singular,
            summary="List all notes in the " + self.model_name_singular,
            path="/notes/list",
            methods=["GET"],
            view_func=self.NoteFunctionality.get_list_func(instance=self),
            response=List[NoteGetSchema],
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

        self.add_api_operation(
            operation_id="create_note_for_" + self.model_name_singular.lower(),
            description="Create a note for the " + self.model_name_singular,
            summary="Create a note for the " + self.model_name_singular,
            path="/notes/create",
            methods=["POST"],
            view_func=self.NoteFunctionality.get_post_func(instance=self),
            response=NoteCreateSchema,
            tags=self.tags,
            auth=self.auth,
            by_alias=True,
        )

    class NoteFunctionality:
        def _get_note_in_instance_or_404(
            model, parent_id: int = None, note_id: int = None
        ) -> Note:
            parent_entity = model.objects.get(pk=parent_id)
            if parent_entity is None:
                raise Http404("Parent entity not found")

            note = parent_entity.notes.get(pk=note_id)

            return note

        def _get_all_notes_in_instance_or_404(model, parent_id: int = None) -> Note:
            parent_entity = model.objects.get(pk=parent_id)
            if parent_entity is None:
                raise Http404("Parent entity not found")

            return parent_entity.notes.all()

        def get_retrieve_note_func(instance: "NotesMixinRouter"):
            def retrieve_func(request, parent_entity_id: int, id: int):
                entity = instance.model.objects.get(pk=parent_entity_id)
                note = entity.notes.get(pk=id)

                if note is None:
                    raise Http404("Note not found")

                return note

            return retrieve_func

        def get_delete_func(instance: "NotesMixinRouter"):
            def delete_func(request, parent_entity_id: int, id: int) -> NoteGetSchema:
                note = get_object_or_404(Note, pk=id)
                note.delete()
                return note

            return delete_func

        def get_put_func(instance: "NotesMixinRouter"):
            def put_func(request, parent_entity_id: int, note_id: int, payload: dict):
                instance = instance.model.objects.get(pk=parent_entity_id)
                note = instance.notes.get(pk=note_id)
                if note is None:
                    raise Http404("Note not found")

                for key, value in payload.items():
                    setattr(note, key, value)
                note.save()

                return note

            return put_func

        def get_list_func(instance: "NotesMixinRouter"):
            def list_func(request, parent_entity_id) -> List[NoteGetSchema]:
                return instance.NoteFunctionality._get_all_notes_in_instance_or_404(
                    model=instance.model, parent_id=parent_entity_id
                )

            return list_func

        def get_post_func(instance: "NotesMixinRouter"):
            def post_func(request, parent_entity_id: int, payload: NoteCreateSchema):
                parent_entity = get_object_or_404(instance.model, pk=parent_entity_id)
                note = Note.objects.create(
                    title=payload.title,
                    content=payload.content,
                    author=request.user.person, 
                    has_personal_information=payload.has_personal_information,
                    created=datetime.now(),
                    modified=datetime.now(),
                )
                parent_entity.notes.add(note)
                return note

            return post_func
