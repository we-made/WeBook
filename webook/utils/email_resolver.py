"""email_resolver.py

Utility functions for resolving user/person from a given email
"""

from typing import Optional

from webook.arrangement.models import Person
from webook.users.models import User


def resolve_email(email_address: str) -> Optional[Person]:
    # person = Person.objects.get(personal_email=email_address)
    person = None

    if person is None:
        try:
            user = User.objects.get(email=email_address)
        except User.DoesNotExist:
            user = None

        if user is not None:
            person = user.person

    return person
