from ..contexts.fullcalendar.context import FullCalendarContext

from django import template
from django.template import Context
from django.template.loader import get_template


register = template.Library()


@register.filter(name="fullcalendar")
def fullcalendar(context: FullCalendarContext):
    context.launch()
    ctx = Context(
        {
            "context": context
        }
    ).flatten()
    template = get_template("fullcalendar/calendar.html")
    return template.render(ctx)
