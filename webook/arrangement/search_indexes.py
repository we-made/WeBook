from haystack import indexes
from webook.arrangement.models import Person

class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    email = indexes.CharField(model_attr='personal_email')
    # social_provider_id = indexes.CharField(model_attr='social_provider_id')
    # social_provider_email = indexes.CharField(model_attr='social_provider_email')

    def get_model(self):
        return Person
    
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_archived=False)