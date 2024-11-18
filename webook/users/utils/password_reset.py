from datetime import datetime, timedelta, timezone
from webook.users.models import User, UserResetPasswordToken
import secrets
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.conf import settings


def perform_password_reset_request(user: User, domain: str):
    """
    Perform the password reset request for the given user.
    """

    if settings.ALLOW_EMAIL_LOGIN is False:
        raise ValueError(
            "Email login is not enabled, and as such password reset is not possible."
        )

    token = secrets.token_urlsafe(6)
    encoded = make_password(token, secrets.token_hex(16))

    password_reset_token = UserResetPasswordToken(
        user=user,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        token=encoded,
    )

    password_reset_token.save()

    context = {
        "email": user.email,
        "domain": domain,
        "site_name": settings.APP_TITLE,
        "code": token,
        "protocol": "https" if domain.startswith("https") else "http",
    }

    # subject = loader.render_to_string(
    #     "registration/password_reset_subject.txt", context
    # )
    body = loader.render_to_string(
        "registration/password_reset_email_code.html", context
    )

    email_message = EmailMultiAlternatives(
        "Tilbakestilling av passord", body, settings.DEFAULT_FROM_EMAIL, [user.email]
    )

    # email_message.attach_alternative(body, "text/html")

    email_message.send()


def complete_password_reset_request(user: User, code: str, new_password: str):
    # We only want to check the latest token generated for this user
    sys_token = UserResetPasswordToken.objects.filter(user=user).order_by("-id").first()

    if sys_token is None:
        raise ValueError("No password reset token found")

    if sys_token.is_used:
        raise ValueError("Token has already been used")

    is_correct = check_password(code, sys_token.token)

    if is_correct:
        user.set_password(new_password)
        user.save()
        sys_token.is_used = True
        sys_token.save()

        body = loader.render_to_string(
            "registration/password_reset_complete.html",
            {"email": user.email, "site_name": settings.APP_TITLE},
        )
        email_message = EmailMultiAlternatives(
            "Passord tilbakestilt",
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email_message.send()
    else:
        raise ValueError("Invalid code")
