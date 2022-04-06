from django.contrib import admin
from .models import (Arrangement, DisplayLayout, Location, Room, Person, Event, Organization, OrganizationType, Article, Audience,
                     BusinessHour, TimelineEvent, ServiceProvidable, ServiceType, Calendar, Note, ConfirmationReceipt, 
                     DisplayLayout, ScreenResource, ScreenGroup)


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
    ServiceProvidable,
    ServiceType,
    Calendar,
    Note,
    ConfirmationReceipt,
    DisplayLayout,
    ScreenResource, 
    ScreenGroup
])
