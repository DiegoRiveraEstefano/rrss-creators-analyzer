from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.campaigns.models import CampaignDeliverable
from rrss_creatos_analyzer.apps.campaigns.models import SponsorCampaign
from rrss_creatos_analyzer.apps.core.choices import DeliverableStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.streams.services import SessionSegmentService
from rrss_creatos_analyzer.apps.streams.services import StreamingSessionService

from .factories import SessionSegmentFactory
from .factories import StreamingSessionFactory

pytestmark = pytest.mark.django_db


class TestStreamingSessionService:
    def test_save_session_calculates_hours_and_earnings(self):
        creator = CreatorFactory()
        start = timezone.now()
        end = start + timedelta(hours=3)

        session = StreamingSessionService.save_session(
            creator=creator,
            session_title="Main Stream",
            platform=PlatformType.TWITCH,
            streamed_at=start,
            ended_at=end,
            ad_revenue=Decimal("50.00"),
            subs_revenue=Decimal("100.00"),
            donations_revenue=Decimal("25.00"),
            bits_or_gifts_revenue=Decimal("25.00"),
            peak_viewers=2000,
            avg_ccv=1200,
        )
        assert session.pk is not None
        assert session.duration_seconds == 10800  # noqa: PLR2004
        assert session.hours_streamed == Decimal("3.00")
        assert session.total_earnings == Decimal("200.00")
        assert session.earnings_per_hour == Decimal("66.67")

    def test_save_session_invalid_dates_raises_error(self):
        creator = CreatorFactory()
        start = timezone.now()
        end = start - timedelta(hours=1)

        with pytest.raises(BusinessLogicError, match="no puede ser anterior"):
            StreamingSessionService.save_session(
                creator=creator,
                streamed_at=start,
                ended_at=end,
            )

    def test_save_session_avg_greater_than_peak_raises_error(self):
        creator = CreatorFactory()
        with pytest.raises(BusinessLogicError, match="debe ser mayor o igual"):
            StreamingSessionService.save_session(
                creator=creator,
                streamed_at=timezone.now(),
                peak_viewers=100,
                avg_ccv=200,
            )

    def test_save_session_negative_revenue_raises_error(self):
        creator = CreatorFactory()
        with pytest.raises(BusinessLogicError, match="no pueden ser negativos"):
            StreamingSessionService.save_session(
                creator=creator,
                streamed_at=timezone.now(),
                ad_revenue=Decimal("-10.00"),
            )

    def test_save_session_sponsored_validation_and_deliverable_link(self):
        creator = CreatorFactory()
        campaign = SponsorCampaign.objects.create(
            brand_name="BrandX",
            campaign_name="Launch",
            campaign_code="BX-01",
            start_date=timezone.localdate(),
        )
        deliverable = CampaignDeliverable.objects.create(
            campaign=campaign,
            creator=creator,
            title="Sponsored Live Stream",
        )

        with pytest.raises(
            BusinessLogicError, match="ingreso de patrocinio mayor a cero",
        ):
            StreamingSessionService.save_session(
                creator=creator,
                streamed_at=timezone.now(),
                is_sponsored=True,
                sponsorship_revenue=Decimal("0.00"),
            )

        session = StreamingSessionService.save_session(
            creator=creator,
            streamed_at=timezone.now(),
            is_sponsored=True,
            sponsorship_revenue=Decimal("500.00"),
            deliverable=deliverable,
        )
        deliverable.refresh_from_db()
        assert deliverable.linked_session == session
        assert deliverable.status == DeliverableStatus.PUBLISHED

    def test_upsert_session_creates_or_updates(self):
        creator = CreatorFactory()
        session1, created = StreamingSessionService.upsert_session(
            creator=creator,
            platform=PlatformType.TWITCH,
            external_stream_id="stream_abc",
            streamed_at=timezone.now(),
            peak_viewers=500,
            avg_ccv=300,
        )
        assert created is True
        assert session1.peak_viewers == 500  # noqa: PLR2004

        session2, created = StreamingSessionService.upsert_session(
            creator=creator,
            platform=PlatformType.TWITCH,
            external_stream_id="stream_abc",
            peak_viewers=800,
        )
        assert created is False
        assert session2.pk == session1.pk
        assert session2.peak_viewers == 800  # noqa: PLR2004

    def test_delete_session(self):
        session = StreamingSessionFactory()
        StreamingSessionService.delete_session(instance=session)
        assert not StreamingSession.objects.filter(pk=session.pk).exists()


class TestSessionSegmentService:
    def test_save_segment_happy_path(self):
        session = StreamingSessionFactory(duration_seconds=7200)
        segment = SessionSegmentService.save_segment(
            session=session,
            game_or_category="League of Legends",
            start_offset_seconds=0,
            duration_seconds=3600,
            peak_viewers=1000,
            avg_ccv=600,
        )
        assert segment.pk is not None

    def test_save_segment_avg_greater_than_peak_raises_error(self):
        session = StreamingSessionFactory(duration_seconds=7200)
        with pytest.raises(BusinessLogicError, match="debe ser mayor o igual"):
            SessionSegmentService.save_segment(
                session=session,
                game_or_category="Chess",
                duration_seconds=1800,
                peak_viewers=50,
                avg_ccv=100,
            )

    def test_save_segment_offset_exceeds_stream_raises_error(self):
        session = StreamingSessionFactory(duration_seconds=3600)
        with pytest.raises(BusinessLogicError, match="no puede exceder la duración"):
            SessionSegmentService.save_segment(
                session=session,
                game_or_category="Minecraft",
                start_offset_seconds=2000,
                duration_seconds=2000,
            )

    def test_save_segment_cumulative_duration_exceeds_stream_raises_error(self):
        session = StreamingSessionFactory(duration_seconds=3600)
        SessionSegmentFactory(
            session=session,
            start_offset_seconds=0,
            duration_seconds=2500,
        )
        with pytest.raises(BusinessLogicError, match="suma de duraciones"):
            SessionSegmentService.save_segment(
                session=session,
                game_or_category="GTA V",
                start_offset_seconds=500,
                duration_seconds=1500,
            )
