from __future__ import annotations

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.demo_baseline import is_baseline_user
from rrss_creatos_analyzer.apps.core.demo_cleanup import DemoCleanupService
from rrss_creatos_analyzer.apps.core.demo_roles import DEMO_USERS_SPEC
from rrss_creatos_analyzer.apps.core.demo_roles import ROLE_DEFINITIONS
from rrss_creatos_analyzer.apps.core.demo_services import DemoSeedService
from rrss_creatos_analyzer.apps.core.models import DemoBaselineRecord
from rrss_creatos_analyzer.apps.core.tasks import cleanup_expired_demo_data_task
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.users.models import User

pytestmark = pytest.mark.django_db


def test_seed_demo_data_is_idempotent_and_registers_baseline():
    summary_first = DemoSeedService.seed_all()
    assert summary_first["roles"] == len(ROLE_DEFINITIONS)
    assert summary_first["users"] == len(DEMO_USERS_SPEC)
    assert DemoBaselineRecord.objects.exists()

    creators_count = Creator.objects.count()
    users_count = User.objects.count()

    DemoSeedService.seed_all()
    assert Creator.objects.count() == creators_count
    assert User.objects.count() == users_count

    out = StringIO()
    call_command("seed_demo_data", "--if-empty", stdout=out)
    assert "skipping seed" in out.getvalue()

    demo_manager = User.objects.get(username="demo_manager")
    assert is_baseline_user(demo_manager) is True
    assert demo_manager.has_perm("creators.view_all_creators")
    assert not demo_manager.is_superuser


def test_seed_demo_data_reset_rebuilds_cleanly():
    DemoSeedService.seed_all()
    out = StringIO()
    call_command("seed_demo_data", "--reset", stdout=out)
    assert "Demo data seeded successfully" in out.getvalue()
    assert User.objects.filter(username="demo_manager").exists()
    assert Creator.objects.filter(handle="novastream").exists()


def test_cleanup_demo_data_preserves_baseline_and_purges_expired():
    DemoSeedService.seed_all()
    old_ts = timezone.now() - timedelta(days=9)

    # Backdate baseline records to verify they are NEVER purged.
    Creator.objects.filter(handle="novastream").update(created_at=old_ts)
    User.objects.filter(username="demo_manager").update(date_joined=old_ts)

    expired_user = User.objects.create_user(
        username="expired_eval_user",
        email="expired@example.com",
        password="TestPassword123!",  # noqa: S106
    )
    User.objects.filter(pk=expired_user.pk).update(date_joined=old_ts)

    fresh_user = User.objects.create_user(
        username="fresh_eval_user",
        email="fresh@example.com",
        password="TestPassword123!",  # noqa: S106
    )

    expired_creator = Creator.objects.create(
        display_name="Expired Creator",
        handle="expired_creator",
        slug="expired-creator",
    )
    Creator.objects.filter(pk=expired_creator.pk).update(created_at=old_ts)

    expired_session = StreamingSession.objects.create(
        creator=expired_creator,
        session_title="Old Stream",
        streamed_at=old_ts,
    )
    StreamingSession.objects.filter(pk=expired_session.pk).update(created_at=old_ts)

    fresh_creator = Creator.objects.create(
        display_name="Fresh Creator",
        handle="fresh_creator",
        slug="fresh-creator",
    )

    dry_summary = DemoCleanupService.purge_expired_data(retention_days=7, dry_run=True)
    assert dry_summary["creators.Creator"] == 1
    assert dry_summary["streams.StreamingSession"] == 1
    assert dry_summary["users.User"] == 1
    assert Creator.objects.filter(pk=expired_creator.pk).exists()

    with override_settings(DEMO_MODE=True, DEMO_DATA_RETENTION_DAYS=7):
        real_summary = cleanup_expired_demo_data_task()

    assert real_summary["creators.Creator"] == 1
    assert real_summary["users.User"] == 1
    assert not Creator.objects.filter(pk=expired_creator.pk).exists()
    assert not StreamingSession.objects.filter(pk=expired_session.pk).exists()
    assert not User.objects.filter(pk=expired_user.pk).exists()

    # Baseline and fresh records remain intact
    assert Creator.objects.filter(handle="novastream").exists()
    assert User.objects.filter(username="demo_manager").exists()
    assert Creator.objects.filter(pk=fresh_creator.pk).exists()
    assert User.objects.filter(pk=fresh_user.pk).exists()


def test_cleanup_command_rejects_invalid_days():
    with pytest.raises(ValueError, match="at least 1"):
        DemoCleanupService.purge_expired_data(retention_days=0)
