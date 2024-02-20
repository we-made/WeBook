from unicodedata import name

from django.urls import path

from webook.arrangement.views.note_views import *

note_urls = [
    path(
        route="note/notes_on_entity",
        view=notes_on_entity_view,
        name="notes_on_entity_component",
    ),
    path(
        route="note/create",
        view=create_note_view,
        name="create_note",
    ),
    path(route="note/<int:entityPk>", view=update_note_view, name="update_note"),
    path(route="note/delete/<int:entityPk>", view=delete_note_view, name="delete_note"),
    path(
        route="note/getNotes",
        view=get_notes_view,
        name="get_notes",
    ),
]
