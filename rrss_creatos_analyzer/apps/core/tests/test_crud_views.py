from http import HTTPStatus

import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

CRUD_LIST_AND_CREATE_URLS = [
    ("core:settings_list", "core:settings_create"),
    ("permissions:role_list", "permissions:role_create"),
    ("members:invitation_list", "members:invitation_create"),
    ("members:assignment_list", "members:assignment_create"),
    ("creators:creator_list", "creators:creator_create"),
    ("creators:channel_list", "creators:channel_create"),
    ("creators:snapshot_list", "creators:snapshot_create"),
    ("contracts:contract_list", "contracts:contract_create"),
    ("imports:batch_list", "imports:batch_create"),
    ("exports:export_list", "exports:export_create"),
    ("streams:session_list", "streams:session_create"),
    ("streams:segment_list", "streams:segment_create"),
    ("videos:video_list", "videos:video_create"),
    ("videos:publication_list", "videos:publication_create"),
    ("videos:relation_list", "videos:relation_create"),
    ("alerts:alert_list", "alerts:alert_create"),
    ("campaigns:campaign_list", "campaigns:campaign_create"),
    ("campaigns:deliverable_list", "campaigns:deliverable_create"),
    ("payouts:payout_list", "payouts:payout_create"),
    ("analytics:snapshot_list", "analytics:snapshot_create"),
    ("audit:audit_list", "audit:audit_create"),
    ("logs:log_list", "logs:log_create"),
    ("monitor:health_list", "monitor:health_create"),
    ("backups:backup_list", "backups:backup_create"),
]


@pytest.mark.parametrize(("list_url", "create_url"), CRUD_LIST_AND_CREATE_URLS)
def test_crud_list_and_create_views_render_for_superuser(
    client,
    list_url: str,
    create_url: str,
):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    res_list = client.get(reverse(list_url))
    assert res_list.status_code == HTTPStatus.OK

    res_create = client.get(reverse(create_url))
    assert res_create.status_code == HTTPStatus.OK


@pytest.mark.parametrize(("list_url", "create_url"), CRUD_LIST_AND_CREATE_URLS)
def test_crud_views_enforce_native_permissions_for_unprivileged_user(
    client,
    list_url: str,
    create_url: str,
):
    user = UserFactory(is_superuser=False, is_staff=False)
    client.force_login(user)

    res_list = client.get(reverse(list_url))
    assert res_list.status_code == HTTPStatus.FORBIDDEN

    res_create = client.get(reverse(create_url))
    assert res_create.status_code == HTTPStatus.FORBIDDEN
