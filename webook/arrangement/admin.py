from django.contrib import admin
from .models import (Arrangement, Location, Room, Person, Event, Organization, OrganizationType, Article, Audience,
                     BusinessHour, TimelineEvent, ServiceProvider, ServiceType, Calendar, Note, ConfirmationReceipt,)


admin.site.register([
    Arrangement,
    Location,
    Room,
    Person,
    Event,
    Organization,
    OrganizationType,
    Article,
    Audience,
    BusinessHour,
    TimelineEvent,
    ServiceProvider,
    ServiceType,
    Calendar,
    Note,
    ConfirmationReceipt
])
