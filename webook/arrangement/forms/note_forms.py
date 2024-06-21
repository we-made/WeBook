from django import forms

from webook.arrangement.models import Note, Person
from webook.utils.meta_utils.typeToModels import getEntityTypeToModelsDict


class BaseNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("title", "content", "has_personal_information")


class CreateNoteForm(BaseNoteForm):
    entityType = forms.CharField()
    entityPk = forms.IntegerField()

    def save(self, author_person: Person):
        note = self.instance
        note.author = author_person
        note.updated_by = author_person
        note.save()

        model = getEntityTypeToModelsDict()[self.cleaned_data["entityType"]]
        model_instance = model.objects.filter(pk=self.cleaned_data["entityPk"]).first()
        model_instance.notes.add(note)
        model_instance.save()


class UpdateNoteForm(BaseNoteForm):
    def save(self, author_person: Person):
        # ToDo: When merging with prod branch, we will use ModelAuditableMixin and can remove this - as it will be done automatically by middleware.
        note = self.instance
        note.updated_by = author_person
        note.save()
