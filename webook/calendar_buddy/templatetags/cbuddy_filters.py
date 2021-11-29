from ..contexts.fullcalendar.context import FullCalendarContext

from django import template
from django.template import Context
from django.template.loader import get_template


register = template.Library()


@register.filter(name="fullcalendar")
def fullcalendar(context: FullCalendarContext):
    """
        Custom filter for the FullCalendar context
        Renders a FullCalendarContext into an actual FullCalendar instance in the front-end
        For example (in Jinja2): {{ my_fc_context | fullcalendar }}

        :param context: The context to render
        :type context: FullCalendar context type
    """

    context.launch()
    ctx = Context(
        {
            "context": context
        }
    ).flatten()
    template = get_template("fullcalendar/calendar.html")
    return template.render(ctx)
