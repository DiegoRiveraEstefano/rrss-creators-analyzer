from __future__ import annotations

from datetime import date
from datetime import time
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from rrss_creatos_analyzer.apps.contracts.models import Contract
from rrss_creatos_analyzer.apps.core.choices import ChannelStatus
from rrss_creatos_analyzer.apps.core.choices import ContractStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorTier
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.choices import TeamResponsibility
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import ChannelSnapshot
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.creators.models import CreatorPersonalInfo
from rrss_creatos_analyzer.apps.members.models import CreatorTeamAssignment
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException

from .demo_baseline import mark_baseline

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from rrss_creatos_analyzer.apps.users.models import User


def seed_creators_and_channels(
    *,
    users: dict[str, User],
    groups: dict[str, Group],
) -> dict[str, object]:
    """Seed baseline creators, personal profiles, team assignments, and channels."""
    now = timezone.now()
    today = timezone.localdate()
    manager = users["demo_manager"]
    analyst = users["demo_analyst"]
    creator_user = users["demo_creator"]

    c_nova, _ = Creator.objects.get_or_create(
        handle="novastream",
        defaults={
            "user": creator_user,
            "manager": manager,
            "display_name": "Nova Stream",
            "slug": "novastream",
            "language_code": "en",
            "main_category": "FPS / Variety",
            "tier": CreatorTier.ELITE,
            "status": CreatorStatus.ACTIVE,
            "joined_company_at": date(2025, 1, 15),
            "bio": "Competitive FPS & variety live streamer.",
        },
    )
    c_kael, _ = Creator.objects.get_or_create(
        handle="kaelplays",
        defaults={
            "manager": manager,
            "display_name": "Kael Plays",
            "slug": "kaelplays",
            "language_code": "es",
            "main_category": "RPG & IRL",
            "tier": CreatorTier.PARTNER,
            "status": CreatorStatus.ACTIVE,
            "joined_company_at": date(2025, 4, 10),
            "bio": "Long-form RPG storytelling and community IRL broadcasts.",
        },
    )
    c_mira, _ = Creator.objects.get_or_create(
        handle="miracrafts",
        defaults={
            "manager": manager,
            "display_name": "Mira Crafts",
            "slug": "miracrafts",
            "language_code": "en",
            "main_category": "Creative & Tech",
            "tier": CreatorTier.STANDARD,
            "status": CreatorStatus.ONBOARDING,
            "joined_company_at": date(2026, 2, 1),
            "bio": "Tech builds, hardware reviews, and short-form tips.",
        },
    )
    for creator, country, city in [
        (c_nova, "US", "Austin"),
        (c_kael, "ES", "Madrid"),
        (c_mira, "CA", "Toronto"),
    ]:
        mark_baseline(creator)
        info, _ = CreatorPersonalInfo.objects.get_or_create(
            creator=creator,
            defaults={
                "legal_full_name": f"{creator.display_name} Demo Legal",
                "contact_email": f"{creator.handle}@demo.example.com",
                "country_code": country,
                "city": city,
            },
        )
        mark_baseline(info)

    assign_m, _ = CreatorTeamAssignment.objects.get_or_create(
        creator=c_nova,
        user=manager,
        responsibility=TeamResponsibility.TALENT_MANAGER,
        defaults={"group": groups["Manager"], "is_primary": True},
    )
    assign_a, _ = CreatorTeamAssignment.objects.get_or_create(
        creator=c_nova,
        user=analyst,
        responsibility=TeamResponsibility.ANALYST,
        defaults={"group": groups["Analyst"], "is_primary": True},
    )
    mark_baseline(assign_m)
    mark_baseline(assign_a)

    ch_nova_tw, _ = Channel.objects.get_or_create(
        creator=c_nova,
        platform=PlatformType.TWITCH,
        platform_channel_id="tw_nova_001",
        defaults={
            "handle": "novastream",
            "channel_name": "NovaStream Live",
            "channel_url": "https://twitch.tv/novastream",
            "is_primary": True,
            "is_verified": True,
            "is_live": True,
            "status": ChannelStatus.ACTIVE,
            "followers_count": 245000,
            "subscribers_count": 4800,
            "paid_subscribers_count": 3200,
            "total_views_count": 12400000,
            "last_stream_at": now - timedelta(hours=4),
        },
    )
    ch_nova_yt, _ = Channel.objects.get_or_create(
        creator=c_nova,
        platform=PlatformType.YOUTUBE,
        platform_channel_id="yt_nova_001",
        defaults={
            "handle": "@novastream",
            "channel_name": "NovaStream Highlights",
            "channel_url": "https://youtube.com/@novastream",
            "is_primary": False,
            "is_verified": True,
            "status": ChannelStatus.ACTIVE,
            "followers_count": 180000,
            "subscribers_count": 180000,
            "total_views_count": 19500000,
        },
    )
    ch_kael_kick, _ = Channel.objects.get_or_create(
        creator=c_kael,
        platform=PlatformType.KICK,
        platform_channel_id="kick_kael_001",
        defaults={
            "handle": "kaelplays",
            "channel_name": "KaelPlays",
            "channel_url": "https://kick.com/kaelplays",
            "is_primary": True,
            "status": ChannelStatus.ACTIVE,
            "followers_count": 96000,
            "subscribers_count": 1450,
            "total_views_count": 4200000,
        },
    )
    ch_mira_tt, _ = Channel.objects.get_or_create(
        creator=c_mira,
        platform=PlatformType.TIKTOK,
        platform_channel_id="tt_mira_001",
        defaults={
            "handle": "@miracrafts",
            "channel_name": "Mira Crafts",
            "channel_url": "https://tiktok.com/@miracrafts",
            "is_primary": True,
            "status": ChannelStatus.ACTIVE,
            "followers_count": 64000,
            "total_views_count": 3100000,
        },
    )
    for channel in (ch_nova_tw, ch_nova_yt, ch_kael_kick, ch_mira_tt):
        mark_baseline(channel)

    for day_offset, delta in [(2, 420), (1, 510), (0, 640)]:
        snap, _ = ChannelSnapshot.objects.get_or_create(
            channel=ch_nova_tw,
            snapshot_date=today - timedelta(days=day_offset),
            defaults={
                "followers_count": 244000 + delta,
                "followers_delta": delta,
                "subscribers_count": 4800,
                "paid_subscribers_count": 3200,
                "total_views_count": 12400000 + delta * 100,
                "views_delta": delta * 100,
            },
        )
        mark_baseline(snap)

    return {
        "c_nova": c_nova,
        "c_kael": c_kael,
        "c_mira": c_mira,
        "ch_nova_tw": ch_nova_tw,
        "ch_nova_yt": ch_nova_yt,
        "ch_kael_kick": ch_kael_kick,
    }


def seed_contracts_and_schedules(
    *,
    users: dict[str, User],
    roster: dict[str, object],
) -> tuple[Contract, CreatorSchedulePattern]:
    """Seed baseline creator contracts, recurring patterns, and compliance records."""
    now = timezone.now()
    today = timezone.localdate()
    manager = users["demo_manager"]
    c_nova: Creator = roster["c_nova"]  # type: ignore[assignment]
    c_kael: Creator = roster["c_kael"]  # type: ignore[assignment]
    ch_nova_tw: Channel = roster["ch_nova_tw"]  # type: ignore[assignment]

    contract_nova, _ = Contract.objects.get_or_create(
        contract_code="DEMO-CNT-2026-001",
        defaults={
            "creator": c_nova,
            "status": ContractStatus.ACTIVE,
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 12, 31),
            "auto_renew": True,
            "base_monthly_retainer": Decimal("1500.00"),
            "stream_creator_split_pct": Decimal("80.00"),
            "stream_agency_split_pct": Decimal("20.00"),
            "video_creator_split_pct": Decimal("70.00"),
            "video_agency_split_pct": Decimal("30.00"),
            "sponsorship_creator_split_pct": Decimal("75.00"),
            "sponsorship_agency_split_pct": Decimal("25.00"),
            "min_monthly_stream_hours": Decimal("80.00"),
            "min_monthly_videos": 8,
            "min_monthly_shorts": 16,
        },
    )
    contract_kael, _ = Contract.objects.get_or_create(
        contract_code="DEMO-CNT-2026-002",
        defaults={
            "creator": c_kael,
            "status": ContractStatus.ACTIVE,
            "start_date": date(2026, 1, 1),
            "base_monthly_retainer": Decimal("800.00"),
            "stream_creator_split_pct": Decimal("80.00"),
            "stream_agency_split_pct": Decimal("20.00"),
            "min_monthly_stream_hours": Decimal("60.00"),
            "min_monthly_videos": 4,
        },
    )
    mark_baseline(contract_nova)
    mark_baseline(contract_kael)

    pattern, _ = CreatorSchedulePattern.objects.get_or_create(
        creator=c_nova,
        title="Prime Evening FPS Stream",
        defaults={
            "channel": ch_nova_tw,
            "platform": PlatformType.TWITCH,
            "rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
            "start_time": time(18, 0),
            "end_time": time(22, 0),
            "planned_duration_minutes": 240,
            "category_or_game": "Valorant",
            "effective_from": date(2026, 1, 1),
            "is_active": True,
        },
    )
    mark_baseline(pattern)

    exc, _ = ScheduleException.objects.get_or_create(
        creator=c_kael,
        title="Studio Hardware Upgrade",
        start_date=today + timedelta(days=5),
        end_date=today + timedelta(days=6),
        defaults={
            "reason_type": ScheduleExceptionReason.TECHNICAL,
            "is_approved": True,
            "approved_by": manager,
            "approved_at": now,
        },
    )
    mark_baseline(exc)

    comp, _ = CreatorScheduleComplianceSummary.objects.get_or_create(
        creator=c_nova,
        year=today.year,
        month=today.month,
        defaults={
            "stipulated_days_count": 12,
            "completed_days_count": 11,
            "stipulated_hours": Decimal("48.00"),
            "actual_hours": Decimal("45.50"),
            "days_compliance_rate_pct": Decimal("91.67"),
            "hours_compliance_rate_pct": Decimal("94.79"),
            "punctuality_rate_pct": Decimal("95.00"),
            "is_compliant": True,
        },
    )
    mark_baseline(comp)

    return contract_nova, pattern
