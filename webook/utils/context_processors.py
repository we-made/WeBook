from django.conf import settings


def settings_context(_request):
    # Put global template variables here.
    return {"DEBUG": settings.DEBUG, "APP_TITLE": settings.APP_TITLE, "APP_LOGO": settings.APP_LOGO,
            "FULLCALENDAR_LICENSE_KEY": settings.FULLCALENDAR_LICENSE_KEY }  # explicit
