from django.forms import Form, ModelChoiceField
from django.forms.fields import ChoiceField

from webook.arrangement.models import Notification


class MarkNotificationAsSeenForm(Form):
    def __init__(self, *args, **kwargs) -> None:
        self.base_fields["notification"].queryset = kwargs.pop("notifications_qs")
        super().__init__(*args, **kwargs)

    notification = ModelChoiceField(
        queryset=Notification.objects.none(),
    )

    def save(self):
        notification: Notification = self.cleaned_data["notification"]

        notification.is_seen = True

        notification.save()
