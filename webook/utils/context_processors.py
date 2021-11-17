from django.conf import settings


def settings_context(_request):
    # Put global template variables here.
    return {"DEBUG": settings.DEBUG, "APP_TITLE": settings.APP_TITLE, "APP_LOGO": settings.APP_LOGO, "ASSET_SERVER_URL": settings.ASSET_SERVER_URL }  # explicit
