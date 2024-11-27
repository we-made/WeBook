from django.db import models
from webook.arrangement.models import Person, Event


class GraphCalendar(models.Model):
    name = models.CharField(max_length=100)
    calendar_id = models.CharField(max_length=100)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SyncedEvent(models.Model):
    """Tracks a synced event between WeBook and Graph API."""

    webook_event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="synced_events"
    )

    graph_event_id = models.CharField(max_length=100)
    graph_calendar = models.ForeignKey(GraphCalendar, on_delete=models.CASCADE)

    # Hash of the event to track changes
    # This is used to check if the event has been updated
    event_hash = models.CharField(max_length=100)

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

    @property
    def is_in_sync(self):
        """Check if the event is in sync."""
        print(
            f"({type(self.webook_event.hash_key())}) {self.webook_event.hash_key()} == ({type(self.event_hash)}) {self.event_hash}"
        )
        return self.webook_event.hash_key() == self.event_hash

    def __str__(self):
        return f"{self.webook_event} - {self.graph_event_id}"
