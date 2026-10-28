from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory

from .factories import SessionSegmentFactory
from .factories import StreamingSessionFactory

pytestmark = pytest.mark.django_db


class TestStreamingSessionModel:
    def test_str_and_get_absolute_url(self):
        session = StreamingSessionFactory(session_title="Special Live Event")
        assert "Special Live Event" in str(session)
        assert session.get_absolute_url() == f"/streams/{session.pk}/"

    def test_clean_validation_end_before_start(self):
        now = timezone.now()
        session = StreamingSessionFactory.build(
            streamed_at=now,
            ended_at=now - timedelta(hours=1),
        )
        with pytest.raises(ValidationError):
            session.clean()

    def test_clean_validation_avg_ccv_greater_than_peak(self):
        session = StreamingSessionFactory.build(
            avg_ccv=1000,
            peak_viewers=500,
        )
        with pytest.raises(ValidationError):
            session.clean()

    def test_clean_validation_sponsored_without_revenue(self):
        session = StreamingSessionFactory.build(
            is_sponsored=True,
            sponsorship_revenue=Decimal("0.00"),
        )
        with pytest.raises(ValidationError):
            session.clean()

    def test_unique_creator_platform_external_id(self):
        creator = CreatorFactory()
        StreamingSessionFactory(
            creator=creator,
            platform=PlatformType.TWITCH,
            external_stream_id="live_12345",
        )
        with pytest.raises(IntegrityError):
            StreamingSessionFactory(
                creator=creator,
                platform=PlatformType.TWITCH,
                external_stream_id="live_12345",
            )


class TestSessionSegmentModel:
    def test_str_and_get_absolute_url(self):
        segment = SessionSegmentFactory(game_or_category="Elden Ring")
        assert "Elden Ring" in str(segment)
        assert segment.get_absolute_url() == f"/streams/segments/{segment.pk}/"

    def test_clean_avg_ccv_greater_than_peak(self):
        segment = SessionSegmentFactory.build(
            avg_ccv=900,
            peak_viewers=800,
        )
        with pytest.raises(ValidationError):
            segment.clean()

    def test_clean_duration_exceeds_session(self):
        session = StreamingSessionFactory(duration_seconds=3600)
        segment = SessionSegmentFactory.build(
            session=session,
            start_offset_seconds=1000,
            duration_seconds=3000,
        )
        with pytest.raises(ValidationError):
            segment.clean()
