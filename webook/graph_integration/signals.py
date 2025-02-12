from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .tasks import synchronize_user_calendar

from webook.arrangement.models import Event, PlanManifest


@receiver(post_save, sender=Event)
def on_event_handler(sender, instance, created, **kwargs):
    if instance.serie:
        return

    people = list(instance.people.all())

    for person in people:
        user = person.user_set.first()
        if user:
            synchronize_user_calendar.delay(user.pk)


@receiver(post_save, sender=PlanManifest)
def on_event_serie_handler(sender, instance, created, **kwargs):
    people = instance.people.all()

    for person in people:
        user = person.user_set.first()
        if user:
            synchronize_user_calendar.delay(user.pk)
