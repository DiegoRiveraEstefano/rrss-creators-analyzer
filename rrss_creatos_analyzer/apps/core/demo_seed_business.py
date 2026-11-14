from __future__ import annotations

from datetime import date
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from rrss_creatos_analyzer.apps.alerts.models import ChannelAlert
from rrss_creatos_analyzer.apps.analytics.models import AnalyticsSnapshot
from rrss_creatos_analyzer.apps.campaigns.models import CampaignDeliverable
from rrss_creatos_analyzer.apps.campaigns.models import SponsorCampaign
from rrss_creatos_analyzer.apps.core.choices import AlertSeverity
from rrss_creatos_analyzer.apps.core.choices import AlertStatus
from rrss_creatos_analyzer.apps.core.choices import AlertType
from rrss_creatos_analyzer.apps.core.choices import CampaignStatus
from rrss_creatos_analyzer.apps.core.choices import DeliverableStatus
from rrss_creatos_analyzer.apps.core.choices import DeliverableType
from rrss_creatos_analyzer.apps.core.choices import PayoutStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.editors.choices import AssignmentStatus
from rrss_creatos_analyzer.apps.editors.choices import EditorAssignmentRole
from rrss_creatos_analyzer.apps.editors.choices import EditorSpecialty
from rrss_creatos_analyzer.apps.editors.choices import EditorStatus
from rrss_creatos_analyzer.apps.editors.choices import EditorType
from rrss_creatos_analyzer.apps.editors.choices import RateModel
from rrss_creatos_analyzer.apps.editors.choices import RevisionStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskPriority
from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskType
from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.models import TaskRevision
from rrss_creatos_analyzer.apps.logs.models import ApplicationLogEntry
from rrss_creatos_analyzer.apps.monitor.models import InstanceHealthCheck
from rrss_creatos_analyzer.apps.payouts.models import CreatorPayout

from .demo_baseline import mark_baseline

if TYPE_CHECKING:
    from rrss_creatos_analyzer.apps.contracts.models import Contract
    from rrss_creatos_analyzer.apps.creators.models import Channel
    from rrss_creatos_analyzer.apps.creators.models import Creator
    from rrss_creatos_analyzer.apps.streams.models import StreamingSession
    from rrss_creatos_analyzer.apps.users.models import User
    from rrss_creatos_analyzer.apps.videos.models import Video


def seed_editors_and_business(
    *,
    users: dict[str, User],
    roster: dict[str, object],
    media: dict[str, object],
    contract_nova: Contract,
) -> dict[str, int]:
    """Seed baseline editors, sponsor campaigns, payouts, alerts, and ops telemetry."""
    now = timezone.now()
    today = timezone.localdate()
    manager = users["demo_manager"]
    finance = users["demo_finance"]
    c_nova: Creator = roster["c_nova"]  # type: ignore[assignment]
    c_kael: Creator = roster["c_kael"]  # type: ignore[assignment]
    ch_kael_kick: Channel = roster["ch_kael_kick"]  # type: ignore[assignment]
    sess_nova: StreamingSession = media["sess_nova"]  # type: ignore[assignment]
    sess_kael: StreamingSession = media["sess_kael"]  # type: ignore[assignment]
    video: Video = media["video"]  # type: ignore[assignment]

    editor, _ = Editor.objects.get_or_create(
        handle="alexcuts",
        defaults={
            "name": "Alex Rivera",
            "slug": "alexcuts",
            "email": "alexcuts@demo.example.com",
            "status": EditorStatus.ACTIVE,
            "editor_type": EditorType.IN_HOUSE,
            "primary_specialty": EditorSpecialty.LONG_FORM,
            "rate_model": RateModel.PER_VIDEO,
            "base_video_rate": Decimal("250.00"),
            "base_short_rate": Decimal("45.00"),
        },
    )
    mark_baseline(editor)

    ed_assign, _ = EditorAssignment.objects.get_or_create(
        editor=editor,
        creator=c_nova,
        role=EditorAssignmentRole.LEAD_EDITOR,
        defaults={
            "status": AssignmentStatus.ACTIVE,
            "is_primary": True,
            "agreed_video_rate": Decimal("250.00"),
            "start_date": date(2026, 1, 1),
        },
    )
    mark_baseline(ed_assign)

    task, _ = EditingTask.objects.get_or_create(
        title="Cut Finals Highlight Reel",
        creator=c_nova,
        editor=editor,
        defaults={
            "video": video,
            "status": TaskStatus.COMPLETED,
            "priority": TaskPriority.HIGH,
            "task_type": TaskType.LONG_FORM_EDIT,
            "assigned_date": today - timedelta(days=4),
            "deadline": today - timedelta(days=2),
            "agreed_cost": Decimal("250.00"),
            "is_paid": True,
            "paid_at": now - timedelta(days=1),
        },
    )
    mark_baseline(task)

    rev, _ = TaskRevision.objects.get_or_create(
        task=task,
        revision_number=1,
        defaults={
            "render_url": "https://cdn.example.com/demo/finals-v1.mp4",
            "change_summary": "Final color pass and audio mastering.",
            "status": RevisionStatus.APPROVED,
            "submitted_at": now - timedelta(days=3),
            "reviewed_at": now - timedelta(days=2),
        },
    )
    mark_baseline(rev)

    campaign, _ = SponsorCampaign.objects.get_or_create(
        campaign_code="DEMO-CMP-2026-HP",
        defaults={
            "account_manager": manager,
            "brand_name": "HyperPulse Peripherals",
            "campaign_name": "Pro Wireless Launch Q2",
            "status": CampaignStatus.ACTIVE,
            "start_date": today - timedelta(days=14),
            "end_date": today + timedelta(days=16),
            "total_budget": Decimal("12000.00"),
            "agency_fee_amount": Decimal("3000.00"),
            "creator_pool_amount": Decimal("9000.00"),
            "target_views_or_impressions": 500000,
        },
    )
    mark_baseline(campaign)

    deliv, _ = CampaignDeliverable.objects.get_or_create(
        campaign=campaign,
        creator=c_nova,
        title="Sponsored Ranked Stream + Pin Link",
        defaults={
            "linked_session": sess_nova,
            "deliverable_type": DeliverableType.SPONSORED_STREAM,
            "platform": PlatformType.TWITCH,
            "due_date": today - timedelta(days=1),
            "completed_at": now - timedelta(days=1),
            "status": DeliverableStatus.PUBLISHED,
            "agreed_creator_payout": Decimal("3500.00"),
            "promo_code": "NOVA20",
            "conversions_count": 318,
        },
    )
    mark_baseline(deliv)

    payout, _ = CreatorPayout.objects.get_or_create(
        creator=c_nova,
        period_year=today.year,
        period_month=today.month,
        defaults={
            "contract": contract_nova,
            "approved_by": finance,
            "status": PayoutStatus.APPROVED,
            "gross_stream_revenue": Decimal("1825.00"),
            "gross_video_revenue": Decimal("2090.00"),
            "gross_sponsorship_revenue": Decimal("3500.00"),
            "base_retainer_amount": Decimal("1500.00"),
            "agency_commission_amount": Decimal("1867.00"),
            "net_creator_payout": Decimal("7048.00"),
            "invoice_reference": "DEMO-INV-2026-001",
        },
    )
    mark_baseline(payout)

    alert, _ = ChannelAlert.objects.get_or_create(
        creator=c_kael,
        title="Background Audio Claim Review",
        defaults={
            "channel": ch_kael_kick,
            "related_session": sess_kael,
            "assigned_to": manager,
            "alert_type": AlertType.COPYRIGHT_CLAIM,
            "severity": AlertSeverity.WARNING,
            "status": AlertStatus.ACTIVE,
            "occurred_at": now - timedelta(hours=12),
            "description": "Demo warning alert for VOD background soundtrack review.",
        },
    )
    mark_baseline(alert)

    analytics_snap, _ = AnalyticsSnapshot.objects.get_or_create(
        cache_key="demo:global:kpi_summary",
        defaults={
            "report_type": "agency_kpi_summary",
            "period_label": f"{today.year}-{today.month:02d}",
            "records_count": 3,
            "payload": {"total_creators": 3, "active_campaigns": 1},
        },
    )
    mark_baseline(analytics_snap)

    log_entry, _ = ApplicationLogEntry.objects.get_or_create(
        event_code="DEMO_SEED_COMPLETE",
        logger_name="rrss_creatos_analyzer.demo",
        defaults={
            "level": "INFO",
            "message": "Baseline demo dataset initialized.",
            "occurred_at": now,
        },
    )
    mark_baseline(log_entry)

    health, _ = InstanceHealthCheck.objects.get_or_create(
        notes="Baseline demo health check",
        defaults={
            "status": "healthy",
            "sqlite_journal_mode": "wal",
            "response_time_ms": Decimal("4.20"),
        },
    )
    mark_baseline(health)

    return {
        "creators": 3,
        "channels": 4,
        "sessions": 2,
        "videos": 1,
        "campaigns": 1,
        "payouts": 1,
    }
