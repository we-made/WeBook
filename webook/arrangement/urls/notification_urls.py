from django.urls import path

from webook.arrangement.views.notification_views import *

notification_urls = [
    path(
        route="notifications/mine",
        view=my_notifications_json_list_view,
        name="my_notifications",
    ),
    path(
        route="notifications/mark_as_seen",
        view=mark_notification_as_seen_view,
        name="mark_notification_as_seen",
    ),
    path(
        route="notifications/mark_all_as_seen",
        view=marK_all_notifications_as_seen_view,
        name="mark_all_notifications_as_seen",
    ),
    path(
        route="notifications/archive/<int:id>",
        view=archive_notification_view,
        name="archive_notification",
    ),
]
