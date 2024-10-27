from haystack import indexes
from webook.users.models import User

class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    email = indexes.CharField(model_attr='email')
    timezone = indexes.CharField(model_attr='timezone')
    is_user_admin = indexes.BooleanField(model_attr='is_user_admin')


    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().objects.all()