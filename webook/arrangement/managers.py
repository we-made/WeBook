from datetime import datetime

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet


class ArchivedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class EventManager(ArchivedManager):
    """Manager for the Event model"""
    
    def get_in_period(self, start: datetime, end: datetime ) -> QuerySet:
        """Get events that happen in a range of time
        
        Args:
            start (datetime): The start of the time range
            end (datetime): The end of the time range

        Returns:
            A QuerySet of the model Events

        Raises:
            TypeError: If start or end is not of type datetime 
            ValueError: If start is greater than or equal to end
        """

        if not isinstance(start, datetime):
            raise TypeError("Start is not a datetime")
        if not isinstance(end, datetime):
            raise TypeError("End is not a datetime")

        if start >= end:
            raise ValueError("Start is equal to or greater than the end of the given range")

        return self.filter(Q(start__lte = end) & Q(end__gte = start))

        
