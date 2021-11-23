from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField



class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # First Name and Last Name Do Not Cover Name Patterns
    # Around the Globe.
    name = models.CharField(
        _("Name of User"), blank=True, max_length=255
    )
    slug = AutoSlugField(populate_from="name", blank=True)

    # def get_absolute_url(self):
    #     return reverse(
    #         "users:detail", kwargs={"username": self.username}
    #     )

    def __str__(self) -> str:
        return self.email
