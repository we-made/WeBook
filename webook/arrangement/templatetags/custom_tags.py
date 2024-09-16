from django import template
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.conf import settings

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    if settings.USE_REDIS:
        cache_key = f"has_group:{user.id}:{group_name}"
        result = cache.get(cache_key)
        if result is not None:
            return result

    group = Group.objects.get(name=group_name)
    has_group = group in user.groups.all()

    if settings.USE_REDIS:
        cache.set(cache_key, has_group, 120)

    return has_group
