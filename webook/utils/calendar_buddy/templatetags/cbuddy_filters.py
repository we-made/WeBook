import os

from webook.utils.calendar_buddy.base import CalendarContext
from webook.utils.calendar_buddy.contexts.fullcalendar.context import FullCalendarContext
from django import template
from django.template import Context
from django.template.loader import get_template


register = template.Library()

@register.filter(name="fullcalendar")
def fullcalendar(context: FullCalendarContext):

    context.launch()

    c = Context(
        {
            "context": context
        }
    ).flatten()
    template = get_template("fullcalendar/calendar.html")
    return template.render(c)
