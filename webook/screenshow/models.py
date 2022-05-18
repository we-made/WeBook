from django.db import models
from django_extensions.db.models import TimeStampedModel
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class ScreenResource(TimeStampedModel):

    class ScreenStatus(models.IntegerChoices):
        AVAILABLE = 0, _('Available')
        UNAVAILABLE = 1, _('Unavailable')

    screen_model = models.CharField(verbose_name=_("Screen Model"), max_length=255, blank=False, null=False)
    items_shown = models.IntegerField(verbose_name=_("Shown Items"), null=False, default=10)
    room = models.ForeignKey(to='arrangement.Room', verbose_name=_("Room Based"), on_delete=models.RESTRICT, null=True, blank=True)
    status = models.IntegerField(default=ScreenStatus.AVAILABLE, verbose_name=_("Screen Status"), choices=ScreenStatus.choices)

    folder_path = models.CharField(verbose_name=_("Folder Path"), max_length=255, blank=False, null=True)
    generated_name = models.CharField(verbose_name=_("Generated Name"), max_length=255, blank=False, null=True)

    slug = AutoSlugField(populate_from="screen_model", unique=True)
    instance_name_attribute_name = "screen_model"
    entity_name_singular = _("ScreenResource")
    entity_name_plural = _("ScreenResources")

    @property
    def resolved_name(self):
        # override template name mixin, as it relies on "name" attribute which is no good in this context. We want to use full_name instead.
        return self.screen_model

    def get_absolute_url(self):
        return reverse(
            "screenshow:screen_detail", kwargs={'slug': self.slug}
        )

    def __str__(self):
        """Return screen resource name"""
        return self.name


class ScreenGroup(TimeStampedModel):
    group_name = models.CharField(verbose_name=_("Group Name"), max_length=255, blank=False, null=False)
    group_name_en = models.CharField(verbose_name=_("Screen Group Name English"), max_length=255,
                                     blank=False, null=True)
    quantity = models.IntegerField(verbose_name=_("Quantity"), null=False, default=10)
    room_preset = models.ForeignKey(to='arrangement.RoomPreset', verbose_name=_("Room Preset"), on_delete=models.RESTRICT, null=True,
                             blank=True)
    screens = models.ManyToManyField(to=ScreenResource, verbose_name=_("Screen Resources"))

    slug = AutoSlugField(populate_from="group_name", unique=True)
    instance_name_attribute_name = "group_name"
    entity_name_singular = _("ScreenGroup")
    entity_name_plural = _("ScreenGroups")

    @property
    def resolved_name(self):
        # override template name mixin, as it relies on "name" attribute which is no good in this context. We want to use full_name instead.
        return self.group_name

    def get_absolute_url(self):
        return reverse(
            "screenshow:screen_group_detail", kwargs={'slug': self.slug}
        )

    def __str__(self):
        """Return screen group name"""
        return self.group_name


class DisplayLayout(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=False, null=False)
    description = models.CharField(verbose_name=_("Description"), max_length=255, blank=True)
    items_shown = models.IntegerField(verbose_name=_("Items Shown"), null=False, default=10)
    is_room_based = models.BooleanField(verbose_name=_("Is Room Based"), default=True)
    all_events = models.BooleanField(verbose_name=_("All Events"), default=True)
    is_active = models.BooleanField(verbose_name=_("Layout Enabled"), default=True)

    screens = models.ManyToManyField(to=ScreenResource, verbose_name=_("Screen Resources"), related_name="layouts")
    groups = models.ManyToManyField(to=ScreenGroup, verbose_name=_("Screen Groups"), related_name="layouts")

    setting = models.ForeignKey(to="DisplayLayoutSetting", verbose_name=_("Display Layout Setting"),
                                on_delete=models.RESTRICT, null=True, blank=True)
    
    slug = AutoSlugField(populate_from="name", unique=True)

    instance_name_attribute_name = "name"
    entity_name_singular = _("DisplayLayout")
    entity_name_plural = _("DisplayLayouts")


    def get_absolute_url(self):
        return reverse(
            "screenshow:layout_detail", kwargs={"slug": self.slug}
        )

    @property
    def resolved_name(self):
        # override template name mixin, as it relies on "name" attribute which is no good in this context. We want to use full_name instead.
        return self.name

    def __str__(self):
        """Return display layout name"""
        return self.name


class DisplayLayoutSetting(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=False, null=False)
    html_template = models.TextField(verbose_name=_("HTML Template"))
    css_template = models.TextField(verbose_name=_("CSS Template"))
    file_output_path = models.TextField(verbose_name=_("File Output Path"), max_length=255, blank=True)

    slug = AutoSlugField(populate_from="name", unique=True)
    entity_name_singular = _("DisplayLayoutSetting")
    entity_name_plural = _("DisplayLayoutSettings")

    def __str__(self):
        """Return display layout name"""
        return self.name
