from django.db import models
from webook.arrangement.models import Person, Event, PlanManifest


class GraphCalendar(models.Model):
    name = models.CharField(max_length=100)
    calendar_id = models.CharField(max_length=100)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SyncedEvent(models.Model):
    """Tracks a synced event between WeBook and Graph API."""

    webook_event = models.ForeignKey(
        Event, on_delete=models.RESTRICT, related_name="synced_events", null=True
    )
    webook_serie_manifest = models.ForeignKey(
        PlanManifest, on_delete=models.RESTRICT, related_name="synced_events", null=True
    )

    graph_event_id = models.CharField(max_length=100)
    graph_calendar = models.ForeignKey(GraphCalendar, on_delete=models.CASCADE)

    # Hash of the event to track changes
    # This is used to check if the event has been updated
    event_hash = models.CharField(max_length=100)

    REPEATING = "repeating"
    SINGLE = "single"

    EVENT_TYPE_CHOICES = [
        (REPEATING, REPEATING),
        (SINGLE, SINGLE),
    ]

    PRE_SYNC = "pre_sync"
    SYNCED = "synced"
    DELETED = "deleted"

    STATE_CHOICES = [
        (PRE_SYNC, PRE_SYNC),
        (SYNCED, SYNCED),
        (DELETED, DELETED),
    ]

    synced_counter = models.PositiveIntegerField(default=0)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=PRE_SYNC)
    event_type = models.CharField(
        max_length=10, choices=EVENT_TYPE_CHOICES, default=SINGLE
    )

    @property
    def is_in_sync(self):
        """Check if the event is in sync."""
        if self.event_type == self.REPEATING:
            self.webook_serie_manifest.hash_key() == self.event_hash
        elif self.event_type == self.SINGLE:
            return self.webook_event.hash_key() == self.event_hash

        raise ValueError(f"Unknown event type: {self.event_type}")

    def __str__(self):
        if self.webook_event:
            return f"(Single Event) {self.webook_event} - {self.graph_event_id}"
        elif self.webook_serie_manifest:
            return f"(Repeating Event) {self.webook_serie_manifest} - {self.graph_event_id}"
        else:
            return f"Unknown Event - {self.graph_event_id}"
