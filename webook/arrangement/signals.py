from django.db.models.signals import post_save
from django.dispatch import receiver

from webook.arrangement.models import Room
from webook.screenshow.models import ScreenResource


@receiver(post_save, sender=Room)
def on_room_create_handler(sender, instance, created, **kwargs):
    if created and instance.has_screen:
        screen_name = "Screen in  " + instance.name
        generated_name = _generate_name(instance.name)
        ScreenResource.objects.create(screen_model=screen_name, room_id=instance.id, generated_name=generated_name,  status=ScreenResource.ScreenStatus.AVAILABLE)
        print("Room Created in database")


def _generate_name(name):
    words = name.split(" ")
    words_lower = [word.lower().replace(",", "").replace(".", "").replace("+", "") for word in words]
    return "_".join(words_lower)
