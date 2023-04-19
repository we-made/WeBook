from typing import Any, Dict, List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from webook.arrangement.forms.notification_forms import MarkNotificationAsSeenForm
from webook.arrangement.models import Notification
from webook.arrangement.views.generic_views.archive_view import JsonArchiveView
from webook.arrangement.views.generic_views.json_form_view import JsonFormView
from webook.arrangement.views.mixins.json_response_mixin import JSONResponseMixin


class MyNotificationsJsonListView(LoginRequiredMixin, ListView, JSONResponseMixin):
    model = Notification

    def get_queryset(self):
        qs = self.request.user.person.notifications.all().order_by("-id")
        return qs

    def transform_queryset(self, queryset) -> List[Dict]:
        result: List[Dict] = []

        if not queryset:
            return result

        keys: List[str] = [
            key for key in queryset[0].__dict__.keys() if not key.startswith("_")
        ]

        for item in queryset:
            d = {}

            for key in keys:
                d[key] = item.__dict__[key]

            result.append(d)

        return result

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        return self.render_to_json_response(
            self.transform_queryset(self.get_queryset()), safe=False
        )


my_notifications_json_list_view = MyNotificationsJsonListView.as_view()


class ArchiveNotificationView(LoginRequiredMixin, JsonArchiveView):
    """View for archiving a single notification
    A notification can only be archived by the user that owns it, or differently put, the person that it is
    addressed to."""

    model = Notification
    pk_url_kwarg = "id"

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        notification_to_delete: Notification = self.get_object()

        if notification_to_delete.to_person != request.user.person:
            raise PermissionError()

        return super().delete(request, *args, **kwargs)


archive_notification_view = ArchiveNotificationView.as_view()


class MarkNotificationAsSeenView(LoginRequiredMixin, JsonFormView):
    form_class = MarkNotificationAsSeenForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        form_kwargs = super().get_form_kwargs()
        form_kwargs["notifications_qs"] = self.request.user.person.notifications.all()

        return form_kwargs

    def form_valid(self, form) -> JsonResponse:
        form.save()
        return super().form_valid(form)


mark_notification_as_seen_view = MarkNotificationAsSeenView.as_view()


class MarkAllNotificationsAsSeenView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs) -> JsonResponse:
        unseen_notifications_qs = self.request.user.person.notifications.filter(
            is_seen=False
        )

        unseen_notification: Notification
        for unseen_notification in unseen_notifications_qs.all():
            unseen_notification.is_seen = True
            unseen_notification.save()

        return JsonResponse({"success": True})


marK_all_notifications_as_seen_view = MarkAllNotificationsAsSeenView.as_view()
