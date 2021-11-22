from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import webook.users.media_pathing as media_pathing


class User(AbstractUser):

    # First Name and Last Name Do Not Cover Name Patterns
    # Around the Globe.
    name = models.CharField(
        _("Name of User"), blank=True, max_length=255
    )

    profile_picture = models.FileField(
        verbose_name="Profile Picture",
        upload_to=media_pathing.profile_picture_path
    )

    def get_absolute_url(self):
        return reverse(
            "users:detail", kwargs={"username": self.username}
        )
