from django import forms

from webook.arrangement.models import Note, Person
from webook.utils.meta_utils.typeToModels import getEntityTypeToModelsDict


class BaseNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = (
            "id",
            "content",
            "has_personal_information"
        )


class CreateNoteForm (BaseNoteForm):
    entityType = forms.CharField()
    entityPk = forms.IntegerField()

    def save(self, author_person: Person):
        note = Note()
        note.content = self.cleaned_data["content"]
        note.has_personal_information = self.cleaned_data["has_personal_information"]
        note.author = author_person
        note.save()

        model = getEntityTypeToModelsDict()[self.cleaned_data["entityType"]]
        model_instance = model.objects.filter(pk=self.cleaned_data["entityPk"]).first()
        model_instance.notes.add(note)
        model_instance.save()


class UpdateNoteForm(BaseNoteForm):
    pass
