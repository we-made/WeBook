from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class AbstractBaseRenderer(ABC):
    @abstractmethod
    def render(self, context: dict, template: str) -> str:
        pass


@dataclass
class Routine:
    template: str

    def render(self, context) -> str:
        return render_to_string(self.template, context)

    def to_mail(self, context: dict) -> EmailMessage:
        return EmailMessage(body=self.render(context))


class MailMessageFactory:
    def __init__(self) -> None:
        self.routines = {}

    class BaseContextFabricator:
        """Fabricator for creating the 'base' context that is present on all routines"""

        def fabricate(self, extra_context: Optional[dict]) -> dict:
            return {
                "ORIGINATOR_FRIENDLY_NAME": settings.APP_TITLE,
                "URL": settings.APP_URL,
                **(extra_context or {}),
            }

    def register_routine(self, key: Any, template: str):
        self.routines[key] = Routine(template=template)

    def send(
        self, routine_key: Any, subject: str, recipients: List[str], context: dict
    ) -> None:
        routine = self.routines[routine_key]

        email_message: EmailMessage = routine.to_mail(context)
        email_message.subject = subject
        email_message.to = recipients

        email_message.send()
