from typing import Any

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)


class MicrosoftPersonAccountAdapter(DefaultSocialAccountAdapter):
    """Custom SocialAccountAdapter for integration with Azure Active Directory / Graph API through AllAuth"""
    pass
    # def pre_social_login(self, request, sociallogin):
    #     """ Invoked after a user successsfully authenticates via the social provider. """
    #     super().pre_social_login(request, sociallogin)


    # def authentication_error(self, *args, **kwargs):
    #     """ Invoked when there is an error in the AUTH cycle """
    #     super().authentication_error(args, kwargs)

