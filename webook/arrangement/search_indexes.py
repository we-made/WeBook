from haystack import indexes
from webook.arrangement.models import Arrangement, Event, Location, Note, Person, Room


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    first_name = indexes.CharField(model_attr="first_name")
    last_name = indexes.CharField(model_attr="last_name")
    email = indexes.CharField(model_attr="personal_email")
    # social_provider_id = indexes.CharField(model_attr='social_provider_id')
    # social_provider_email = indexes.CharField(model_attr='social_provider_email')

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr="title")
    title_en = indexes.CharField(model_attr="title_en", null=True)
    is_resolution = indexes.BooleanField(model_attr="is_resolution")
    start = indexes.DateTimeField(model_attr="start")
    end = indexes.DateTimeField(model_attr="end")
    all_day = indexes.BooleanField(model_attr="all_day", null=True)
    display_text = indexes.CharField(model_attr="display_text", null=True)
    display_text_en = indexes.CharField(model_attr="display_text_en", null=True)

    def get_model(self):
        return Event

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)


class ArrangementIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name")
    name_en = indexes.CharField(model_attr="name_en", null=True)
    meeting_place = indexes.CharField(model_attr="meeting_place", null=True)
    meeting_place_en = indexes.CharField(model_attr="meeting_place_en", null=True)

    def get_model(self):
        return Arrangement

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)


class LocationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name")

    def get_model(self):
        return Location

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)


class RoomIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr="name")
    name_en = indexes.CharField(model_attr="name_en", null=True)
    is_exclusive = indexes.BooleanField(model_attr="is_exclusive")
    max_capacity = indexes.IntegerField(model_attr="max_capacity")
    has_screen = indexes.BooleanField(model_attr="has_screen")

    def get_model(self):
        return Room

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    has_personal_information = indexes.BooleanField(
        model_attr="has_personal_information"
    )
    author = indexes.CharField(model_attr="author")

    def get_model(self):
        return Note

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)
