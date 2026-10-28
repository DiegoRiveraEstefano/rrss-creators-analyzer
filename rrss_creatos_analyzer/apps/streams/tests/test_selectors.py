from decimal import Decimal

import pytest

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.streams.selectors import SessionSegmentSelector
from rrss_creatos_analyzer.apps.streams.selectors import StreamingSessionSelector
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

from .factories import SessionSegmentFactory
from .factories import StreamingSessionFactory

pytestmark = pytest.mark.django_db


class TestStreamingSessionSelector:
    def test_get_visible_queryset_for_creator_user(self):
        user = UserFactory()
        creator = CreatorFactory(user=user)
        session = StreamingSessionFactory(creator=creator)
        other_session = StreamingSessionFactory()

        qs = StreamingSessionSelector.get_visible_queryset(user=user)
        assert session in qs
        assert other_session not in qs

    def test_get_visible_queryset_for_superuser(self):
        admin_user = UserFactory(is_superuser=True)
        session = StreamingSessionFactory()
        other_session = StreamingSessionFactory()

        qs = StreamingSessionSelector.get_visible_queryset(user=admin_user)
        assert session in qs
        assert other_session in qs

    def test_get_category_performance_stats(self):
        user = UserFactory(is_superuser=True)
        StreamingSessionFactory(
            game_or_category="Valorant",
            hours_streamed=Decimal("4.00"),
            avg_ccv=1000,
            peak_viewers=2000,
            total_earnings=Decimal("200.00"),
            platform=PlatformType.TWITCH,
        )
        StreamingSessionFactory(
            game_or_category="Valorant",
            hours_streamed=Decimal("2.00"),
            avg_ccv=1200,
            peak_viewers=2200,
            total_earnings=Decimal("150.00"),
            platform=PlatformType.TWITCH,
        )

        stats = StreamingSessionSelector.get_category_performance_stats(
            user=user,
            platform=PlatformType.TWITCH,
        )
        assert len(stats) >= 1
        item = next(s for s in stats if s["game_or_category"] == "Valorant")
        assert item["total_sessions"] == 2  # noqa: PLR2004
        assert item["total_hours"] == Decimal("6.00")


class TestSessionSegmentSelector:
    def test_get_visible_queryset_for_creator_user(self):
        user = UserFactory()
        creator = CreatorFactory(user=user)
        session = StreamingSessionFactory(creator=creator)
        segment = SessionSegmentFactory(session=session)
        other_segment = SessionSegmentFactory()

        qs = SessionSegmentSelector.get_visible_queryset(user=user)
        assert segment in qs
        assert other_segment not in qs
