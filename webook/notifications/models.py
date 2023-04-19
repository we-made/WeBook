# from django.db import models
# from django_extensions.db.models import TimeStampedModel


# class Notification(TimeStampedModel):
#     title = models.CharField(verbose_name="Title", max_length=256)

#     body = models.CharField(verbose_name="Body", max_length=5024)

#     INFO = "info"
#     SUCCESS = "success"
#     DANGER = "danger"
#     WARNING = "warning"
#     PRIMARY = "primary"
#     DARK = "dark"

#     CATEGORY_OF_SEVERITY_CHOICES = (
#         (INFO, "Info"),
#         (SUCCESS, "Success"),
#         (DANGER, "Danger"),
#         (WARNING, "Warning"),
#         (PRIMARY, "Primary"),
#         (DARK, "Dark"),
#     )

#     category_of_severity = models.TextChoices(
#         choices=CATEGORY_OF_SEVERITY_CHOICES, default=INFO, max_length=20
#     )

#     originator = models.CharField(max_length=512)

#     observed = models.BooleanField(default=False)
