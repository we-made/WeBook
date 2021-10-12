from django.db import models
from django_extensions.db.models import TimeStampedModel


class Audience(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "audiences"

    def __str__(self):
        return self.name


class Arrangement(TimeStampedModel):
    name = models.CharField("name", max_length=255)

    audience = models.ForeignKey(Audience, on_delete=models.CASCADE)

    starts = models.DateField("starts")
    ends = models.DateField("ends")

    timeline_events = models.ManyToManyField("TimelineEvent")

    owners = models.ManyToManyField("Person")

    class Meta:
        db_table = "arrangements"

    def __str__(self):
        return self.name


class Location (TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "locations"

    def __str__(self):
        return self.name


class Room(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField("name", max_length=128)

    class Meta:
        db_table = "rooms"

    def __str__(self):
        return self.name


class Article(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "articles"

    def __str__(self):
        return self.name


class OrganizationType(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "organizationtypes"

    def __str__(self):
        return self.name


class TimelineEvent (TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    content = models.CharField("content", max_length=1024)

    def __str__(self):
        return self.content


class ServiceType(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("name", max_length=255)

    def __str__(self):
        return self.name


class BusinessHour(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    start_of_business_hours = models.TimeField("StartOfBusinessHours")
    end_of_business_hours = models.TimeField("EndOfBusinessHours")

    def __str__(self):
        return f"{self.start_of_business_hours} - {self.end_of_business_hours}"


class Calendar(TimeStampedModel):
    # TODO: Make connection between owner (Person)
    id = models.IntegerField("id", primary_key=True)
    name = models.CharField("name", max_length=255)
    is_personal = models.BooleanField("ispersonal", default=True)

    people_resources = models.ManyToManyField("Person")
    room_resources = models.ManyToManyField("Room")

    def __str__(self):
        return self.name


class Note(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    author = models.ForeignKey('Person', on_delete=models.RESTRICT)
    content = models.TextField("content", max_length=1024)

    confirmation = models.ForeignKey("ConfirmationReceipt", on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return self.content


class ConfirmationReceipt (TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    guid = models.CharField("Guid", max_length=68)
    requested_by = models.ForeignKey("Person", on_delete=models.RESTRICT)
    sent_to = models.CharField("SentTo", max_length=255)
    confirmed = models.BooleanField("Confirmed", default=False)
    sent_when = models.DateTimeField("SentWhen")
    confirmed_when = models.DateTimeField("ConfirmedWhen")

    def __str__(self):
        return f"{self.requested_by.get_name()} petitioned {self.sent_to} for a confirmation at STAMP."


class Person(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    personal_email = models.CharField("PersonalEmail", max_length=255, blank=False, null=False)
    first_name = models.CharField("FirstName", max_length=255)
    middle_name = models.CharField("MiddleName", max_length=255, blank=True)
    last_name = models.CharField("LastName", max_length=255)
    birth_date = models.DateField("BirthDate", null=True, blank=True)

    business_hours = models.ForeignKey(BusinessHour, on_delete=models.RESTRICT, null=True, blank=True)
    notes = models.ManyToManyField(Note)

    def __str__(self):
        return ' '.join(name for name in (self.first_name, self.middle_name, self.last_name) if name)

    class Meta:
        db_table = "people"


class Organization(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    organization_number = models.IntegerField("Organization Number", null=True, blank=True)
    name = models.CharField("name", max_length=255)
    organization_type = models.ForeignKey(OrganizationType, on_delete=models.RESTRICT)

    notes = models.ManyToManyField(Note)
    members = models.ManyToManyField(Person)

    def __str__(self):
        return self.name


class ServiceProvider(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    service_name = models.CharField("ServiceName", max_length=255)
    service_type = models.ForeignKey(ServiceType, on_delete=models.RESTRICT)
    organization = models.ForeignKey(Organization, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.service_name} of type {self.service_type} provided by {self.organization.name}"


class Event(TimeStampedModel):
    id = models.IntegerField("id", primary_key=True)
    title = models.CharField("title", max_length=255)
    start = models.DateTimeField("start", null=False)
    end = models.DateTimeField("end", null=False)
    sequence_guid = models.CharField("sequence_guid", max_length=40, null=True, blank=True)
    arrangement = models.ForeignKey(Arrangement, on_delete=models.CASCADE)

    people = models.ManyToManyField(Person)
    rooms = models.ManyToManyField(Room)
    articles = models.ManyToManyField(Article)
    notes = models.ManyToManyField(Note)

    class Meta:
        db_table = "events"

    def __str__(self):
        return f"{self.title} ({self.start} - {self.end})"


class EventService(TimeStampedModel):
    # TODO: Connect to receipt
    id = models.IntegerField("id", primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.RESTRICT)
    notes = models.ManyToManyField(Note)
    associated_people = models.ManyToManyField(Person)
