from django.contrib import admin
from django.contrib.auth.models import Group

from webook.arrangement.forms.group_admin import GroupAdminForm
from .models import (
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
)

admin.site.register(
    [
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
    ]
)

# Unregister the original Group admin.
admin.site.unregister(Group)

# Create a new Group admin.
class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ["permissions"]


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
