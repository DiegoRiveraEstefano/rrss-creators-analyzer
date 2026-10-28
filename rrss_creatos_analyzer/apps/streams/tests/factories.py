from __future__ import annotations

from decimal import Decimal

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.streams.models import SessionSegment
from rrss_creatos_analyzer.apps.streams.models import StreamingSession


class StreamingSessionFactory(DjangoModelFactory[StreamingSession]):
    creator = factory.SubFactory(CreatorFactory)
    channel = factory.SubFactory(ChannelFactory)
    session_title = factory.Sequence(lambda n: f"Stream Session #{n}")
    game_or_category = "Just Chatting"
    platform = PlatformType.TWITCH
    streamed_at = factory.LazyFunction(timezone.now)
    duration_seconds = 7200
    hours_streamed = Decimal("2.00")
    peak_viewers = 1500
    avg_ccv = 800
    total_earnings = Decimal("150.00")
    earnings_per_hour = Decimal("75.00")

    class Meta:
        model = StreamingSession


class SessionSegmentFactory(DjangoModelFactory[SessionSegment]):
    session = factory.SubFactory(StreamingSessionFactory)
    game_or_category = "Valorant"
    start_offset_seconds = 0
    duration_seconds = 3600
    avg_ccv = 850
    peak_viewers = 1200

    class Meta:
        model = SessionSegment
