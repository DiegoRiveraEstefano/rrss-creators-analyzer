from http import HTTPStatus

import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.audit.models import AuditEvent
from rrss_creatos_analyzer.apps.core.models import CompanySettings
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_auditlog_records_creation_and_update():
    settings = CompanySettings.objects.create(
        company_name="Audit Agency",
        legal_name="Audit Agency S.A.",
        default_currency="EUR",
    )
    entries = AuditEvent.objects.filter(object_pk=str(settings.pk))
    assert entries.count() == 1
    create_entry = entries.first()
    assert create_entry is not None
    assert create_entry.action == 0

    settings.legal_name = "Audit Agency Corp."
    settings.save()

    entries = AuditEvent.objects.filter(object_pk=str(settings.pk))
    expected_entry_count = 2
    assert entries.count() == expected_entry_count
    update_entry = entries.order_by("-timestamp").first()
    assert update_entry is not None
    assert update_entry.action == 1
    assert "Audit Agency S.A." in str(update_entry.changes_display_dict)
    assert "Audit Agency Corp." in str(update_entry.changes_display_dict)


def test_auditlog_views_display_events_and_diff(client):
    admin = UserFactory(is_superuser=True, is_staff=True)
    client.force_login(admin)

    creator = Creator.objects.create(
        display_name="Audited Streamer",
        handle="audited_streamer",
        slug="audited-streamer",
    )
    creator.display_name = "Audited Streamer Updated"
    creator.save()

    entry = AuditEvent.objects.filter(object_pk=str(creator.pk)).first()
    assert entry is not None

    res_list = client.get(reverse("audit:audit_list"))
    assert res_list.status_code == HTTPStatus.OK
    assert "Audited Streamer" in res_list.rendered_content

    res_detail = client.get(entry.get_absolute_url())
    assert res_detail.status_code == HTTPStatus.OK
    assert "Detalle de Cambios" in res_detail.rendered_content
