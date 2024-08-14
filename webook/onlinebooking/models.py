from datetime import datetime
from typing import Optional
from django.db import models
from webook.arrangement.managers import ArchivedManager
from webook.arrangement.models import Audience, Person
from django_extensions.db.models import TimeStampedModel
from webook.api.models import ServiceAccount


# TODO: Fix to not duplicate
class ArchiveableMixin(models.Model):
    objects = ArchivedManager()
    all_objects = models.Manager()

    def archive(self, person_archiving_this: Optional[Person] = None):
        """Archive this object"""
        self.is_archived = True
        self.archived_by = person_archiving_this
        self.archived_when = datetime.now()

        on_archive = getattr(self, "on_archive", None)
        if callable(on_archive):
            on_archive(person_archiving_this)

        self.save()

    is_archived = models.BooleanField(verbose_name="Is archived", default=False)

    archived_by = models.ForeignKey(
        verbose_name="Archived by",
        related_name="%(class)s_archived_by",
        to=Person,
        null=True,
        on_delete=models.RESTRICT,
    )

    archived_when = models.DateTimeField(verbose_name="Archived when", null=True)

    class Meta:
        abstract = True


class OnlineBookingSettings(models.Model):
    title_format = models.CharField(max_length=255)

    allowed_audiences = models.ManyToManyField(Audience)

    class Unit(models.TextChoices):
        MINUTES = "minutes", "Minutes" 
        HOURS = "hours", "Hours"
        DAYS = "days", "Days"
        WEEKS = "weeks", "Weeks"
        MONTHS = "months", "Months"
        YEARS = "years", "Years"

    offset_unit = models.CharField(
        max_length=10, choices=Unit.choices, default=Unit.MINUTES
    )
    offset = models.PositiveIntegerField(default=0)
    duration_unit = models.CharField(
        max_length=10, choices=Unit.choices, default=Unit.MINUTES
    )
    duration_amount = models.PositiveIntegerField(default=15)


class OnlineBooking(TimeStampedModel, ArchiveableMixin):
    school = models.ForeignKey(
        "School", on_delete=models.RESTRICT, related_name="bookings"
    )

    # Segment is only set if the county that the school is in has city_segment_enabled
    segment = models.ForeignKey("CitySegment", on_delete=models.RESTRICT, null=True)
    segment_text = models.CharField(max_length=255, null=True)

    audience_type = models.ForeignKey(Audience, on_delete=models.RESTRICT)

    visitors_count = models.PositiveIntegerField()

    # Audit purposes
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField()

    # The service account that was used to make the booking
    service_account = models.ForeignKey(
        ServiceAccount, on_delete=models.RESTRICT, null=True
    )


class School(TimeStampedModel, ArchiveableMixin):
    name = models.CharField(max_length=255)
    county = models.ForeignKey(
        "County", on_delete=models.RESTRICT, related_name="schools_in_county"
    )
    audience = models.ForeignKey(
        Audience,
        on_delete=models.RESTRICT,
        related_name="schools",
        blank=True,
        null=True,
    )
    city_segment = models.ForeignKey(
        "CitySegment",
        on_delete=models.RESTRICT,
        related_name="schools_in_segment",
        null=True,
    )

    def on_archive(self, person_archiving_this):
        # Archive all bookings for this school
        for booking in self.bookings.all():
            booking.archive(person_archiving_this)

    def __str__(self):
        return self.name


class County(TimeStampedModel, ArchiveableMixin):
    county_number = models.PositiveIntegerField(
        verbose_name="County number", unique=True
    )
    name = models.CharField(max_length=255)
    city_segment_enabled = models.BooleanField(default=False)

    def on_archive(self, person_archiving_this):
        # Archive all schools in this county
        for school in self.schools_in_county.all():
            school.archive(person_archiving_this)

        # Archive all city segments in this county
        for segment in self.city_segments.all():
            segment.archive(person_archiving_this)

    def __str__(self):
        return self.name


class CitySegment(TimeStampedModel, ArchiveableMixin):
    name = models.CharField(max_length=255)
    county = models.ForeignKey(
        "County", on_delete=models.CASCADE, related_name="city_segments"
    )

    def on_archive(self, person_archiving_this):
        # Archive all schools in this segment
        for school in self.schools_in_segment.all():
            school.archive(person_archiving_this)

    def __str__(self):
        return self.name
