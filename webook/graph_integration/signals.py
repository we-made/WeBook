from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .tasks import synchronize_user_calendar
from webook.systask.task_manager_factory import create_task_manager
from webook.arrangement.models import Event, PlanManifest


@receiver(post_save, sender=Event)
def on_event_handler(sender, instance, created, **kwargs):
    if instance.serie:
        return

    people = list(instance.people.all())

    for person in people:
        user = person.user_set.first()
        if user:
            task_manager = create_task_manager()
            task_manager.enqueue_task(
                task_name="synchronize_user_calendar",
                task_args={"user_pk": user.pk},
                task_kwargs={},
            )
            # synchronize_user_calendar.delay(user.pk)


@receiver(post_save, sender=PlanManifest)
def on_event_serie_handler(sender, instance, created, **kwargs):
    people = instance.people.all()

    for person in people:
        user = person.user_set.first()
        if user:
            task_manager = create_task_manager()
            task_manager.enqueue_task(
                task_name="synchronize_user_calendar",
                task_args={"user_pk": user.pk},
                task_kwargs={},
            )
            # synchronize_user_calendar.delay(user.pk)
