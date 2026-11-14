from __future__ import annotations

from http import HTTPStatus

import pytest
from captcha.models import CaptchaStore
from django.test import override_settings
from django.urls import reverse

from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.users.forms import UserResetPasswordForm
from rrss_creatos_analyzer.apps.users.forms import UserSignupForm
from rrss_creatos_analyzer.apps.users.models import User

pytestmark = pytest.mark.django_db


def test_signup_assigns_default_manager_role_without_403(client):
    with override_settings(
        DEMO_MODE=True,
        CAPTCHA_ENABLED=False,
        ACCOUNT_EMAIL_VERIFICATION="none",
    ):
        response = client.post(
            reverse("account_signup"),
            {
                "username": "new_eval_user",
                "email": "neweval@example.com",
                "password1": "StrongDemoPass987!",
                "password2": "StrongDemoPass987!",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("home")

        user = User.objects.get(username="new_eval_user")
        assert user.groups.filter(name="Manager").exists()
        assert client.get(reverse("creators:creator_list")).status_code == HTTPStatus.OK
        assert client.get(reverse("streams:session_list")).status_code == HTTPStatus.OK


def test_signup_with_creator_demo_role_creates_linked_creator(client):
    with override_settings(
        DEMO_MODE=True,
        CAPTCHA_ENABLED=False,
        ACCOUNT_EMAIL_VERIFICATION="none",
    ):
        response = client.post(
            reverse("account_signup"),
            {
                "username": "creator_eval",
                "email": "creatoreval@example.com",
                "password1": "StrongDemoPass987!",
                "password2": "StrongDemoPass987!",
                "demo_role": "Creator",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        user = User.objects.get(username="creator_eval")
        assert user.groups.filter(name="Creator").exists()
        assert Creator.objects.filter(user=user).exists()


def test_signup_and_password_reset_enforce_captcha_when_enabled(client):
    with override_settings(DEMO_MODE=True, CAPTCHA_ENABLED=True):
        form_get = client.get(reverse("account_signup"))
        assert form_get.status_code == HTTPStatus.OK
        assert "captcha_0" in form_get.content.decode()

        bad_form = UserSignupForm(
            data={
                "username": "bot_user",
                "email": "bot@example.com",
                "password1": "StrongDemoPass987!",
                "password2": "StrongDemoPass987!",
                "captcha_0": "invalid-hash",
                "captcha_1": "WRONG",
            },
        )
        assert not bad_form.is_valid()
        assert "captcha" in bad_form.errors

        bad_reset = UserResetPasswordForm(
            data={
                "email": "someone@example.com",
                "captcha_0": "invalid-hash",
                "captcha_1": "WRONG",
            },
        )
        assert not bad_reset.is_valid()
        assert "captcha" in bad_reset.errors

        hashkey = CaptchaStore.generate_key()
        challenge = CaptchaStore.objects.get(hashkey=hashkey).response
        ok_resp = client.post(
            reverse("account_signup"),
            {
                "username": "human_eval",
                "email": "humaneval@example.com",
                "password1": "StrongDemoPass987!",
                "password2": "StrongDemoPass987!",
                "demo_role": "Analyst",
                "captcha_0": hashkey,
                "captcha_1": challenge,
            },
        )
        assert ok_resp.status_code == HTTPStatus.FOUND
        assert User.objects.filter(username="human_eval").exists()
