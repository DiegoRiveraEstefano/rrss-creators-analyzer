from __future__ import annotations

from datetime import time
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import ImportBatchType
from rrss_creatos_analyzer.apps.core.choices import ImportStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import PublicationType
from rrss_creatos_analyzer.apps.core.choices import VideoFormat
from rrss_creatos_analyzer.apps.core.choices import VideoRelationType
from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.exports.models import ExportJob
from rrss_creatos_analyzer.apps.imports.models import ImportBatch
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.streams.models import SessionSegment
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.videos.models import Video
from rrss_creatos_analyzer.apps.videos.models import VideoPublication
from rrss_creatos_analyzer.apps.videos.models import VideoRelation

from .demo_baseline import mark_baseline

if TYPE_CHECKING:
    from rrss_creatos_analyzer.apps.creators.models import Channel
    from rrss_creatos_analyzer.apps.creators.models import Creator
    from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
    from rrss_creatos_analyzer.apps.users.models import User


def seed_streams_and_videos(
    *,
    users: dict[str, User],
    roster: dict[str, object],
    pattern: CreatorSchedulePattern,
) -> dict[str, object]:
    """Seed baseline import/export jobs, streaming sessions, segments, and videos."""
    now = timezone.now()
    today = timezone.localdate()
    manager = users["demo_manager"]
    analyst = users["demo_analyst"]
    c_nova: Creator = roster["c_nova"]  # type: ignore[assignment]
    c_kael: Creator = roster["c_kael"]  # type: ignore[assignment]
    ch_nova_tw: Channel = roster["ch_nova_tw"]  # type: ignore[assignment]
    ch_nova_yt: Channel = roster["ch_nova_yt"]  # type: ignore[assignment]
    ch_kael_kick: Channel = roster["ch_kael_kick"]  # type: ignore[assignment]

    batch, _ = ImportBatch.objects.get_or_create(
        filename="demo_streams_batch_2026.csv",
        defaults={
            "uploaded_by": analyst,
            "batch_type": ImportBatchType.STREAMS,
            "source_platform": PlatformType.TWITCH,
            "total_rows": 24,
            "valid_rows": 24,
            "created_rows": 24,
            "status": ImportStatus.COMPLETED,
            "completed_at": now - timedelta(days=1),
        },
    )
    mark_baseline(batch)

    export_job, _ = ExportJob.objects.get_or_create(
        file_path="exports/demo_monthly_streams_summary.csv",
        defaults={
            "requested_by": analyst,
            "report_type": "streams",
            "export_format": "csv",
            "status": "completed",
            "rows_exported": 24,
        },
    )
    mark_baseline(export_job)

    sess_nova, _ = StreamingSession.objects.get_or_create(
        creator=c_nova,
        platform=PlatformType.TWITCH,
        external_stream_id="demo-stream-nova-001",
        defaults={
            "channel": ch_nova_tw,
            "import_batch": batch,
            "session_title": "Ranked Finals & Community Games",
            "game_or_category": "Valorant",
            "streamed_at": now - timedelta(days=1, hours=5),
            "ended_at": now - timedelta(days=1, hours=1),
            "duration_seconds": 14400,
            "hours_streamed": Decimal("4.00"),
            "peak_viewers": 6850,
            "avg_ccv": 4120,
            "unique_viewers": 18400,
            "live_views_count": 32500,
            "chat_messages_count": 48200,
            "unique_chatters_count": 3900,
            "new_followers": 620,
            "new_subscriptions": 145,
            "ad_revenue": Decimal("420.00"),
            "subs_revenue": Decimal("725.00"),
            "donations_revenue": Decimal("180.00"),
            "sponsorship_revenue": Decimal("500.00"),
            "total_earnings": Decimal("1825.00"),
            "earnings_per_hour": Decimal("456.25"),
            "is_sponsored": True,
        },
    )
    sess_kael, _ = StreamingSession.objects.get_or_create(
        creator=c_kael,
        platform=PlatformType.KICK,
        external_stream_id="demo-stream-kael-001",
        defaults={
            "channel": ch_kael_kick,
            "session_title": "Elden Ring Marathon Night",
            "game_or_category": "Elden Ring",
            "streamed_at": now - timedelta(days=2, hours=4),
            "ended_at": now - timedelta(days=2, hours=1),
            "duration_seconds": 10800,
            "hours_streamed": Decimal("3.00"),
            "peak_viewers": 2400,
            "avg_ccv": 1580,
            "unique_viewers": 7900,
            "live_views_count": 12400,
            "new_followers": 210,
            "subs_revenue": Decimal("310.00"),
            "donations_revenue": Decimal("95.00"),
            "total_earnings": Decimal("405.00"),
            "earnings_per_hour": Decimal("135.00"),
        },
    )
    mark_baseline(sess_nova)
    mark_baseline(sess_kael)

    seg1, _ = SessionSegment.objects.get_or_create(
        session=sess_nova,
        game_or_category="Just Chatting",
        start_offset_seconds=0,
        defaults={"duration_seconds": 3600, "avg_ccv": 3400, "peak_viewers": 4100},
    )
    seg2, _ = SessionSegment.objects.get_or_create(
        session=sess_nova,
        game_or_category="Valorant",
        start_offset_seconds=3600,
        defaults={"duration_seconds": 10800, "avg_ccv": 4360, "peak_viewers": 6850},
    )
    mark_baseline(seg1)
    mark_baseline(seg2)

    slot, _ = CreatorScheduleSlot.objects.get_or_create(
        creator=c_nova,
        scheduled_date=today - timedelta(days=1),
        scheduled_start_time=time(18, 0),
        defaults={
            "channel": ch_nova_tw,
            "schedule_pattern": pattern,
            "scheduled_end_time": time(22, 0),
            "planned_duration_minutes": 240,
            "planned_hours": Decimal("4.00"),
            "title": "Prime Evening FPS Stream",
            "category_or_game": "Valorant",
            "status": ScheduleSlotStatus.COMPLETED,
            "actual_streaming_session": sess_nova,
            "actual_duration_minutes": 240,
            "actual_hours": Decimal("4.00"),
            "compliance_rate_pct": Decimal("100.00"),
        },
    )
    mark_baseline(slot)

    video, _ = Video.objects.get_or_create(
        internal_code="DEMO-VID-001",
        creator=c_nova,
        defaults={
            "assigned_editor": manager,
            "title": "Radiant Clutch Breakdown & Highlights",
            "category": "Esports",
            "content_format": VideoFormat.LONG_FORM,
            "duration_seconds": 840,
            "production_cost": Decimal("150.00"),
            "editing_cost": Decimal("250.00"),
            "thumbnail_cost": Decimal("60.00"),
            "total_production_cost": Decimal("460.00"),
            "status": VideoStatus.PUBLISHED,
            "target_release_date": today - timedelta(days=2),
        },
    )
    mark_baseline(video)

    pub, _ = VideoPublication.objects.get_or_create(
        video=video,
        platform=PlatformType.YOUTUBE,
        platform_post_id="yt_demo_pub_001",
        defaults={
            "creator": c_nova,
            "channel": ch_nova_yt,
            "published_title": "How We Won the Finals (Full Breakdown)",
            "publication_type": PublicationType.STANDARD,
            "published_at": now - timedelta(days=2),
            "status": PublicationStatus.PUBLISHED,
            "views_count": 148000,
            "unique_viewers_count": 121000,
            "impressions_count": 1150000,
            "click_through_rate": Decimal("8.40"),
            "likes_count": 12400,
            "comments_count": 940,
            "watch_time_hours": Decimal("14200.00"),
            "retention_rate_pct": Decimal("58.20"),
            "engagement_rate": Decimal("9.10"),
            "ad_revenue": Decimal("890.00"),
            "sponsorship_revenue": Decimal("1200.00"),
            "estimated_revenue": Decimal("2090.00"),
            "rpm_estimated": Decimal("6.01"),
        },
    )
    mark_baseline(pub)

    vrel, _ = VideoRelation.objects.get_or_create(
        source_video=video,
        target_session=sess_nova,
        relation_type=VideoRelationType.DERIVED_FROM_LIVE,
        defaults={"description": "Highlights extracted from Ranked Finals stream."},
    )
    mark_baseline(vrel)

    return {
        "sess_nova": sess_nova,
        "sess_kael": sess_kael,
        "video": video,
    }
