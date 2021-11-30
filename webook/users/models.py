from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import webook.users.media_pathing as media_path

class User(AbstractUser):

    # First Name and Last Name Do Not Cover Name Patterns
    # Around the Globe.
    name = models.CharField(
        _("Name of User"), blank=True, max_length=255
    )

    profile_picture = models.ImageField(
        name="profile_picture",
        verbose_name=_("Profile Picture"),
        upload_to=media_path.profile_picture_path,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse(
            "users:detail", kwargs={"username": self.username}
        )
