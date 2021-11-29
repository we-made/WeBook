from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class Audience(TimeStampedModel):
    """Audience represents a target audience, and is used for categorical purposes.

    :param name: The name of the audience
    :type name: str.

    :param icon_class: The CSS class of the icon used to represent this audience in views
    :type name: str
    """
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    icon_class = models.CharField(verbose_name=_("Icon Class"), max_length=255, blank=True)

    def __str__(self):
        """Return audience name"""
        return self.name


class Arrangement(TimeStampedModel):
    """Arrangements are in practice a sequence of events, or an arrangement of events. Arrangements have events
     that happen in a concerted nature, and share the same purpose and or context. A realistic example of an arrangement
     could be an exhibition, which may have events stretching over a large timespan, but which have a shared nature,
     which is of especial organizational interest

     :param name: The name of the arrangement
     :type name: str.

     :param audience: The classification of the audience that this arrangement is geared towards
     :type audience: Audience.

     :param starts: The start of the arrangement, note that this does not concern the underlying events
     :type starts: date.

     :param ends: The end of the arrangement, note that this does not concern the underlying events
     :type ends: date

     :param timeline_events: Events on the timeline of this arrangement
     :type timeline_events: TimelineEvent.

     :param owners: Owners of this arrangement, owners are privileged and responsible for the arrangement
     :type owners: Person.

     :param people_participants: The people who are participating in this arrangement, may connect to an o
                                 organization_participant
     :type people_participants: Person.

     :param organization_participants: The organizations who are participating in this arrangement
     :type organization_participants: Organization.
     """
    name = models.CharField(verbose_name=_("Name"), max_length=255)

    audience = models.ForeignKey(to=Audience, on_delete=models.CASCADE)

    starts = models.DateField(verbose_name=_("Starts"))
    ends = models.DateField(verbose_name=_("Ends"))

    timeline_events = models.ManyToManyField(to="TimelineEvent")

    owners = models.ManyToManyField(to="Person")

    people_participants = models.ManyToManyField(to="Person", related_name="participating_in")
    organization_participants = models.ManyToManyField(to="Organization", related_name="participating_in")

    def __str__(self):
        """Return arrangement name"""
        return self.name


class Location (TimeStampedModel):
    """Location represents a physical location, for instance a building.
    In practice a location is a group of rooms, primarily helpful in contextualization and filtering

    :param name: The name of the location
    :type name: str.
    """
    name = models.CharField(verbose_name=_("Name"), max_length=255)

    def __str__(self):
        """Return location name"""
        return self.name


class Room(TimeStampedModel):
    """Room represents a physical real-world room. All rooms belong to a location.

    :param location: The location that this room belongs to
    :type location: Location.

    :param name: The name of the room
    :type name: str.
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_("Name"), max_length=128)

    def __str__(self):
        """Return room name"""
        return self.name


class Article(TimeStampedModel):
    """An article is a consumable entity, on the same level in terms of being a resource as room and person.
    In practice an article could for instance be a projector, or any other sort of inanimate physical entity

    :param name: The name of the article
    :type name: str.
    """

    name = models.CharField(verbose_name=_("Name"), max_length=255)

    def __str__(self):
        """Return article name"""
        return self.name


class OrganizationType(TimeStampedModel):
    """An organization type is an arbitrary classification that is applicable to organizations
    For example non-profit organizations, or public organizations. This is for categorical purposes.

    :param name: The name of the organization type
    :type name: str.
    """
    name = models.CharField(verbose_name=_("Name"), max_length=255)

    def __str__(self):
        """Return name of organizationtype"""
        return self.name


class TimelineEvent (TimeStampedModel):
    """A timeline event model represents an event on a timeline, not to be confused with an event on a calendar, which
    is represented by the Event model.

    :param content: The content of this event, to be displayed in the timeline
    :type content: str.

    :param stamp: The date and time the event happened
    :type stamp: datetime.
    """

    content = models.CharField(verbose_name=_("Content"), max_length=1024)
    stamp = models.DateTimeField(verbose_name=_("Stamp"), null=False)

    def __str__(self):
        """Return content"""
        return self.content


class ServiceType(TimeStampedModel):
    """A service type is a type categorization of service providers

    :param name: The name of the service type
    :type name: str.
    """
    name = models.CharField(verbose_name=_("Name"), max_length=255)

    def __str__(self):
        """Return service type name"""
        return self.name


class BusinessHour(TimeStampedModel):
    """A business hour model represents a from-to record keeping track of businesshours
    Primarily used visually to differentiate between business times, and outside of business times, in for instance
    the calendar. May apply to resources.

    :param start_of_business_hours: When business hours begin
    :type start_of_business_hours: Time.

    :param end_of_business_hours: When business hours end
    :type end_of_business_hours: Time.

    """

    start_of_business_hours = models.TimeField(verbose_name=_("Start Of Business Hours"))
    end_of_business_hours = models.TimeField(verbose_name=_("End Of Business Hours"))

    def __str__(self):
        """Return from and to business hours"""
        return f"{self.start_of_business_hours} - {self.end_of_business_hours}"


class Calendar(TimeStampedModel):
    """Represents an implementation, or a version of a calendar. Calendars are built based on resources,
    namely which resources are wanted to be included. May be personal to a select user, or globally shared and
    available for all users

    :param owner: The owner of this calendar
    :type owner: Person.

    :param name: The name of the calendar, used for descriptive purposes
    :type name: str.

    :param is_personal: Designates whether not the calendar is a personal calendar, or a global one, accessible by all.
    :type is_personal: bool.

    :param people_resources: The person resources included in this calendar view
    :type people_resources: Person.

    :param room_resources: The room resources included in this calendar view
    :type room_resources: Room.
    """

    owner = models.ForeignKey(to="Person", on_delete=models.RESTRICT, related_name="owners")

    name = models.CharField(verbose_name=_("Name"), max_length=255)
    is_personal = models.BooleanField(verbose_name=_("Is Personal"), default=True)

    people_resources = models.ManyToManyField(to="Person")
    room_resources = models.ManyToManyField(to="Room")

    def __str__(self):
        """Return calendar name"""
        return self.name


class Note(TimeStampedModel):
    """Notes are annotations that can be associated with other key models in the application. The practical purpose
    is to annotate information on these associated models.

    :param author: The author who wrote this note
    :type author: Person

    :param content: The actual content of the note
    :type content: str.

    :param confirmation: The confirmation, or receipt, associated with this note. Can be null if no receipt was
                         requested.
    :type confirmation: ConfirmationReceipt

    """

    author = models.ForeignKey(to='Person', on_delete=models.RESTRICT)
    content = models.TextField(verbose_name=_("Content"), max_length=1024)

    confirmation = models.ForeignKey(to="ConfirmationReceipt", on_delete=models.RESTRICT, null=True)

    def __str__(self):
        """Return contents of note"""
        return self.content


class ConfirmationReceipt (TimeStampedModel):
    """Confirmation receipts are used to petition a person to confirm something, and allows a tracked
    record of confirmation

    :param guid: GUID to be used in URLs sent out to users in confirmation requests
    :type guid: str.

    :param requested_by: The person who requested confirmation
    :type requested_by: Person.

    :param sent_to: The email the confirmation request was sent to
    :type sent_to: str.

    :param confirmed: Whether the confirmation request has been confirmed or not
    :type confirmed: bool.

    :param sent_when: When the confirmation request was sent
    :type sent_when: datetime.

    :param confirmed_when: When the confirmation request was confirmed
    :type confirmed_when: datetime.

    """

    guid = models.CharField(verbose_name=_("Guid"), max_length=68, unique=True, db_index=True)
    requested_by = models.ForeignKey(to="Person", on_delete=models.RESTRICT)
    sent_to = models.CharField(verbose_name=_("SentTo"), max_length=255)
    confirmed = models.BooleanField(verbose_name=_("Confirmed"), default=False)
    sent_when = models.DateTimeField(verbose_name=_("SentWhen"), null=True)
    confirmed_when = models.DateTimeField(verbose_name=_("ConfirmedWhen"), null=True)

    def __str__(self):
        """Return description of receipt"""
        return f"{self.requested_by} petitioned {self.sent_to} for a confirmation at STAMP."


class Person(TimeStampedModel):
    """Represents a person entity. Does not represent a user however.

    :param personal_email: Email of the person
    :type personal_email: str.

    :param first_name: Firstname of the person
    :type first_name: str.

    :param middle_name: Middle name of the person, optional
    :type middle_name: str.

    :param last_name: Lastname of the person
    :type last_name: str.

    :param birth_date: When the person was born, optional
    :type birth_date: date.

    :param business_hours: The business hours of this person (working hours)
    :type business_hours: BusinessHour.

    :param notes: Notes written about this person
    :type notes: Note.
    """
    personal_email = models.CharField(verbose_name=_("PersonalEmail"), max_length=255, blank=False, null=False)
    first_name = models.CharField(verbose_name=_("FirstName"), max_length=255)
    middle_name = models.CharField(verbose_name=_("MiddleName"), max_length=255, blank=True)
    last_name = models.CharField(verbose_name=_("LastName"), max_length=255)
    birth_date = models.DateField(verbose_name=_("BirthDate"), null=True, blank=True)

    business_hours = models.ForeignKey(to=BusinessHour, on_delete=models.RESTRICT, null=True, blank=True)
    notes = models.ManyToManyField(to=Note)

    def __str__(self):
        """Return full person name"""
        return ' '.join(name for name in (self.first_name, self.middle_name, self.last_name) if name)


class Organization(TimeStampedModel):
    """ Organizations represent real world organizations

    :param organization_number: The organization number associated with this organization - if any
    :type organization_number: int.

    :param name: The name of the organization
    :type name: str.

    :param organization_type: The type of this organization
    :type name: OrganizationType.

    :param notes: The notes associated with this organization
    :type name: Note.

    :param members: The members of this organization
    :type name: Person
    """
    organization_number = models.IntegerField(verbose_name=_("Organization Number"), null=True, blank=True)
    name = models.CharField(verbose_name=_("Name"), max_length=255)
    organization_type = models.ForeignKey(to=OrganizationType, on_delete=models.RESTRICT)

    notes = models.ManyToManyField(to=Note)
    members = models.ManyToManyField(to=Person)

    def __str__(self):
        """Return organization name"""
        return self.name


class ServiceProvider(TimeStampedModel):
    """The service provider provides services that
    can be consumed by events. An organization may provide multiple
    services, and thus be represented through multiple service provider records.

    :param service_name: Name of service this provider provides
    :type service_name: str.

    :param service_type: The type, or classification, of service provided
    :type service_type: ServiceType.

    :param organization: The organization that provides this service
    :type organization: Organization.
    """

    service_name = models.CharField(verbose_name=_("ServiceName"), max_length=255)
    service_type = models.ForeignKey(to=ServiceType, on_delete=models.RESTRICT)
    organization = models.ForeignKey(to=Organization, on_delete=models.RESTRICT)

    def __str__(self):
        """Return description of service provider"""
        return f"{self.service_name} of type {self.service_type} provided by {self.organization.name}"


class Event(TimeStampedModel):
    """The event model represents an event, or happening that takes place in a set span of time, and which may
    reserve certain resources for use in that span of time (such as a room, or a person etc..).

    :param title: The title of the event
    :type title: str.

    :param start: The date and time that the event begins
    :type start: datetime.

    :param end: The date and time that the event ends
    :type end: datetime.

    :param all_day: Designates if the event is a allday event (shown in the allday section in fullcalendar)
    :type all_day: bool.

    :param sequence_guid: If the event is a part of a recurring set it will be assigned a GUID that can uniquely
                          identify all members of the recurring set.
    :type sequence_guid: guid.

    :param arrangement: The arrangement that this event is connected to, is optional
    :type arrangement: Arrangement.

    :param people: The people that are assigned to this event
    :type people: Person.

    :param rooms: The rooms that are assigned to this event
    :type rooms: Room.

    :param articles: The articles that are assigned to this event
    :type articles: Article.

    :param notes: The notes that are written on/about this event
    :type notes: Note.

    """

    title = models.CharField(verbose_name=_("Title"), max_length=255)
    start = models.DateTimeField(verbose_name=_("Start"), null=False)
    end = models.DateTimeField(verbose_name=_("End"), null=False)
    all_day = models.BooleanField(verbose_name=_("AllDay"))
    sequence_guid = models.CharField(verbose_name=_("SequenceGuid"), max_length=40, null=True, blank=True)
    arrangement = models.ForeignKey(to=Arrangement, on_delete=models.CASCADE)

    people = models.ManyToManyField(to=Person)
    rooms = models.ManyToManyField(to=Room)
    articles = models.ManyToManyField(to=Article)
    notes = models.ManyToManyField(to=Note)

    def __str__(self):
        """Return title of event, with start and end times"""
        return f"{self.title} ({self.start} - {self.end})"


class EventService(TimeStampedModel):
    """
    The event service model is a many-to-many mapping relationship between Event and ServiceProvider

    :param receipt: A receipt or confirmation, most likely sent to the service provider, that confirms that they will
                    provide the service
    :type receipt: ConfirmationReceipt

    :param event: The event that the service is being provided to
    :type event: Event.

    :param service_provider: The service provider that is providing the service
    :type service_provider: ServiceProvider.

    :param notes: Notes concerning the provision of the service
    :type notes: Note.

    :param associated_people: The people who will render these services
    :type associated_people: Person.
    """

    receipt = models.ForeignKey(to=ConfirmationReceipt, on_delete=models.RESTRICT)
    event = models.ForeignKey(to=Event, on_delete=models.RESTRICT)
    service_provider = models.ForeignKey(to=ServiceProvider, on_delete=models.RESTRICT)
    notes = models.ManyToManyField(to=Note)
    associated_people = models.ManyToManyField(to=Person)
