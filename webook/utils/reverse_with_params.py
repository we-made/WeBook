from django.utils.http import urlencode
from django.urls import reverse


def reverse_with_params(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url