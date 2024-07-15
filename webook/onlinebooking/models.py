from django.db import models
from webook.arrangement.models import Audience
from django_extensions.db.models import TimeStampedModel
from webook.api.models import ServiceAccount


class OnlineBookingSettings(models.Model):
    allowed_audiences = models.ManyToManyField(Audience)


class OnlineBooking(TimeStampedModel):
    school = models.ForeignKey("School", on_delete=models.RESTRICT)

    # Segment is only set if the county that the school is in has city_segment_enabled
    segment = models.ForeignKey("CitySegment", on_delete=models.RESTRICT, null=True)

    audience_type = models.ForeignKey(Audience, on_delete=models.RESTRICT)

    # Audit purposes
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    # The service account that was used to make the booking
    service_account = models.ForeignKey(ServiceAccount, on_delete=models.RESTRICT)


class School(TimeStampedModel):
    name = models.CharField(max_length=255)
    county = models.ForeignKey(
        "County", on_delete=models.CASCADE, related_name="schools_in_county"
    )
    city_segment = models.ForeignKey(
        "CitySegment", on_delete=models.CASCADE, related_name="schools_in_segment"
    )

    def __str__(self):
        return self.name


class County(TimeStampedModel):
    name = models.CharField(max_length=255)
    city_segment_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CitySegment(TimeStampedModel):
    name = models.CharField(max_length=255)
    county = models.ForeignKey("County", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
