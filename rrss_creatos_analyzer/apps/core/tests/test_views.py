from __future__ import annotations

from http import HTTPStatus
from unittest import mock

import pytest
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.test import APIClient
from rest_framework.throttling import AnonRateThrottle

from rrss_creatos_analyzer.apps.core.demo_services import DemoSeedService
from rrss_creatos_analyzer.apps.users.models import User

pytestmark = pytest.mark.django_db


def test_quick_demo_login_disabled_outside_demo_mode(client):
    with override_settings(DEMO_MODE=False):
        response = client.post(reverse("demo_login"), {"role": "Manager"})
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_quick_demo_login_auto_seeds_and_grants_role_access(client):
    with override_settings(DEMO_MODE=True):
        response = client.post(reverse("demo_login"), {"role": "Manager"})
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == reverse("home")

        creators_resp = client.get(reverse("creators:creator_list"))
        assert creators_resp.status_code == HTTPStatus.OK

        bad_resp = client.post(reverse("demo_login"), {"role": "Company Admin"})
        assert bad_resp.status_code == HTTPStatus.FOUND
        assert bad_resp.url == reverse("account_login")


def test_baseline_demo_account_cannot_change_password_or_email(client):
    DemoSeedService.seed_all()
    with override_settings(DEMO_MODE=True):
        client.post(reverse("demo_login"), {"role": "Manager"})
        pw_resp = client.post(
            reverse("account_change_password"),
            {
                "oldpassword": "wrong",
                "password1": "NewStrongPass99!",
                "password2": "NewStrongPass99!",
            },
        )
        assert pw_resp.status_code == HTTPStatus.FORBIDDEN

        email_resp = client.post(
            reverse("account_email"),
            {"email": "hijack@example.com", "action_add": ""},
        )
        assert email_resp.status_code == HTTPStatus.FORBIDDEN


def test_backup_mutations_blocked_for_non_superusers_in_demo_mode(client):
    DemoSeedService.seed_all()
    admin_user = User.objects.get(username="demo_admin")
    with override_settings(DEMO_MODE=True):
        client.force_login(admin_user)
        resp = client.post(
            reverse("backups:backup_create"),
            {"backup_name": "evil", "file_path": "/tmp/evil.db"},  # noqa: S108
        )
        assert resp.status_code == HTTPStatus.FORBIDDEN


def test_quick_demo_login_rate_limit_returns_429(client):
    cache.clear()
    DemoSeedService.seed_all()
    with override_settings(DEMO_MODE=True, RATELIMIT_ENABLE=True):
        for _ in range(15):
            resp = client.post(reverse("demo_login"), {"role": "Analyst"})
            assert resp.status_code == HTTPStatus.FOUND

        throttled = client.post(reverse("demo_login"), {"role": "Analyst"})
        assert throttled.status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert b"Too Many Requests" in throttled.content
    cache.clear()


def test_drf_anon_throttle_returns_429():
    cache.clear()
    api_client = APIClient()
    url = reverse("obtain_auth_token")

    class StrictAnonThrottle(AnonRateThrottle):
        rate = "2/min"

    with mock.patch.object(
        ObtainAuthToken,
        "throttle_classes",
        [StrictAnonThrottle],
    ):
        assert api_client.post(url, {}).status_code == HTTPStatus.BAD_REQUEST
        assert api_client.post(url, {}).status_code == HTTPStatus.BAD_REQUEST
        third = api_client.post(url, {})
        assert third.status_code == HTTPStatus.TOO_MANY_REQUESTS
    cache.clear()
