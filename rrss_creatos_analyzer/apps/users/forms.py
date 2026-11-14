from __future__ import annotations

from typing import Any

from allauth.account.forms import ResetPasswordForm
from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from .models import User

DEMO_ROLE_CHOICES: tuple[tuple[str, Any], ...] = (
    ("Manager", _("Manager — Full operational roster & content access")),
    ("Analyst", _("Analyst — Read-only analytics, imports & exports")),
    ("Finance", _("Finance — Contracts, campaigns & creator payouts")),
    ("Creator", _("Creator — Personal creator dashboard & payouts only")),
)


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """Signup form with optional demo role selector and CAPTCHA verification."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if getattr(settings, "DEMO_MODE", False):
            default_role = getattr(settings, "DEMO_DEFAULT_SIGNUP_GROUP", "Manager")
            self.fields["demo_role"] = forms.ChoiceField(
                label=_("Role to Evaluate"),
                choices=DEMO_ROLE_CHOICES,
                initial=default_role,
                required=False,
                help_text=_(
                    "Automatically assigns permissions so you can test the "
                    "platform right away.",
                ),
            )
        if getattr(settings, "CAPTCHA_ENABLED", False):
            self.fields["captcha"] = CaptchaField(
                label=_("Security Verification"),
            )


class UserResetPasswordForm(ResetPasswordForm):
    """Password reset form protected by CAPTCHA when enabled."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if getattr(settings, "CAPTCHA_ENABLED", False):
            self.fields["captcha"] = CaptchaField(
                label=_("Security Verification"),
            )


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
