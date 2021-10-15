from django.db import models
from django_extensions.db.models import TimeStampedModel


class Audience(TimeStampedModel):
    """Audience model"""
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "audiences"

    def __str__(self):
        """Return audience name"""
        return self.name


class Arrangement(TimeStampedModel):
    """Arrangement model"""
    name = models.CharField("name", max_length=255)

    audience = models.ForeignKey(Audience, on_delete=models.CASCADE)

    starts = models.DateField("starts")
    ends = models.DateField("ends")

    timeline_events = models.ManyToManyField("TimelineEvent")

    owners = models.ManyToManyField("Person")

    class Meta:
        db_table = "arrangements"

    def __str__(self):
        """Return arrangement name"""
        return self.name


class Location (TimeStampedModel):
    """Location model"""
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "locations"

    def __str__(self):
        """Return location name"""
        return self.name


class Room(TimeStampedModel):
    """Room model"""
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField("name", max_length=128)

    class Meta:
        db_table = "rooms"

    def __str__(self):
        """Return room name"""
        return self.name


class Article(TimeStampedModel):
    """Article model"""
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "articles"

    def __str__(self):
        """Return article name"""
        return self.name


class OrganizationType(TimeStampedModel):
    """Organization type model"""
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "organizationtypes"

    def __str__(self):
        """Return name of organizationtype"""
        return self.name


class TimelineEvent (TimeStampedModel):
    """Timeline event model"""
    content = models.CharField("content", max_length=1024)

    class Meta:
        db_table = "timelineevents"

    def __str__(self):
        """Return content"""
        return self.content


class ServiceType(TimeStampedModel):
    """ServiceType model"""
    name = models.CharField("name", max_length=255)

    class Meta:
        db_table = "servicetypes"

    def __str__(self):
        """Return service type name"""
        return self.name


class BusinessHour(TimeStampedModel):
    """Business hour model"""
    start_of_business_hours = models.TimeField("StartOfBusinessHours")
    end_of_business_hours = models.TimeField("EndOfBusinessHours")

    class Meta:
        db_table = "businesshours"

    def __str__(self):
        """Return from and to business hours"""
        return f"{self.start_of_business_hours} - {self.end_of_business_hours}"


class Calendar(TimeStampedModel):
    """Calendar model"""
    # TODO: Make connection between owner (Person)
    name = models.CharField("name", max_length=255)
    is_personal = models.BooleanField("ispersonal", default=True)

    people_resources = models.ManyToManyField("Person")
    room_resources = models.ManyToManyField("Room")

    class Meta:
        db_table = "calendars"

    def __str__(self):
        """Return calendar name"""
        return self.name


class Note(TimeStampedModel):
    """Note model"""
    author = models.ForeignKey('Person', on_delete=models.RESTRICT)
    content = models.TextField("content", max_length=1024)

    confirmation = models.ForeignKey("ConfirmationReceipt", on_delete=models.RESTRICT, null=True)

    class Meta:
        db_table = "Notes"

    def __str__(self):
        """Return contents of note"""
        return self.content


class ConfirmationReceipt (TimeStampedModel):
    """Confirmation receipt model"""
    guid = models.CharField("Guid", max_length=68)
    requested_by = models.ForeignKey("Person", on_delete=models.RESTRICT)
    sent_to = models.CharField("SentTo", max_length=255)
    confirmed = models.BooleanField("Confirmed", default=False)
    sent_when = models.DateTimeField("SentWhen")
    confirmed_when = models.DateTimeField("ConfirmedWhen")

    class Meta:
        db_table = "confirmationreceipts"

    def __str__(self):
        """Return description of receipt"""
        return f"{self.requested_by.get_name()} petitioned {self.sent_to} for a confirmation at STAMP."


class Person(TimeStampedModel):
    """Person model"""
    personal_email = models.CharField("PersonalEmail", max_length=255, blank=False, null=False)
    first_name = models.CharField("FirstName", max_length=255)
    middle_name = models.CharField("MiddleName", max_length=255, blank=True)
    last_name = models.CharField("LastName", max_length=255)
    birth_date = models.DateField("BirthDate", null=True, blank=True)

    business_hours = models.ForeignKey(BusinessHour, on_delete=models.RESTRICT, null=True, blank=True)
    notes = models.ManyToManyField(Note)

    class Meta:
        db_table = "people"

    def __str__(self):
        """Return full person name"""
        return ' '.join(name for name in (self.first_name, self.middle_name, self.last_name) if name)


class Organization(TimeStampedModel):
    """Organization model"""
    organization_number = models.IntegerField("Organization Number", null=True, blank=True)
    name = models.CharField("name", max_length=255)
    organization_type = models.ForeignKey(OrganizationType, on_delete=models.RESTRICT)

    notes = models.ManyToManyField(Note)
    members = models.ManyToManyField(Person)

    class Meta:
        db_table = "organizations"

    def __str__(self):
        """Return organization name"""
        return self.name


class ServiceProvider(TimeStampedModel):
    """Service provider model"""
    service_name = models.CharField("ServiceName", max_length=255)
    service_type = models.ForeignKey(ServiceType, on_delete=models.RESTRICT)
    organization = models.ForeignKey(Organization, on_delete=models.RESTRICT)

    class Meta:
        db_table = "serviceproviders"

    def __str__(self):
        """Return description of service provider"""
        return f"{self.service_name} of type {self.service_type} provided by {self.organization.name}"


class Event(TimeStampedModel):
    """Event model"""
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
        """Return title of event, with start and end times"""
        return f"{self.title} ({self.start} - {self.end})"


class EventService(TimeStampedModel):
    """Event service model"""
    # TODO: Connect to receipt
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.RESTRICT)
    notes = models.ManyToManyField(Note)
    associated_people = models.ManyToManyField(Person)

    class Meta:
        db_table = "eventservices"
