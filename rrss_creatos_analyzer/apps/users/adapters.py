from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.shortcuts import resolve_url

from .services import UserService

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from rrss_creatos_analyzer.apps.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        if getattr(settings, "DEMO_MODE", False):
            return resolve_url("home")
        return super().get_login_redirect_url(request)

    def get_signup_redirect_url(self, request: HttpRequest) -> str:
        if getattr(settings, "DEMO_MODE", False):
            return resolve_url("home")
        return super().get_signup_redirect_url(request)

    def save_user(
        self,
        request: HttpRequest,
        user: User,
        form: typing.Any,
        commit: bool = True,  # noqa: FBT001, FBT002
    ) -> User:
        user = super().save_user(request, user, form, commit=commit)
        if commit:
            cleaned_data = getattr(form, "cleaned_data", {})
            role_name = cleaned_data.get("demo_role")
            UserService.assign_default_role(user=user, role_name=role_name)
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user

    def save_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        form: typing.Any = None,
    ) -> User:
        user = super().save_user(request, sociallogin, form=form)
        UserService.assign_default_role(user=user)
        return user
