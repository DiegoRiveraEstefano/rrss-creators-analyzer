from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.streams.forms import SessionSegmentForm
from rrss_creatos_analyzer.apps.streams.forms import StreamingSessionForm

from .factories import StreamingSessionFactory

pytestmark = pytest.mark.django_db


class TestStreamingSessionForm:
    def test_form_valid(self):
        creator = CreatorFactory()
        channel = ChannelFactory(creator=creator)
        now = timezone.now()
        data = {
            "creator": creator.pk,
            "channel": channel.pk,
            "platform": PlatformType.TWITCH,
            "session_title": "Daily Stream",
            "game_or_category": "Minecraft",
            "streamed_at": now,
            "ended_at": now + timedelta(hours=2),
            "duration_seconds": 7200,
            "peak_viewers": 1000,
            "avg_ccv": 500,
            "unique_viewers": 800,
            "live_views_count": 1200,
            "chat_messages_count": 300,
            "unique_chatters_count": 150,
            "new_followers": 20,
            "new_subscriptions": 5,
            "gifted_subscriptions": 2,
            "raids_received": 1,
            "ad_revenue": Decimal("10.00"),
            "subs_revenue": Decimal("25.00"),
            "donations_revenue": Decimal("5.00"),
            "bits_or_gifts_revenue": Decimal("5.00"),
            "sponsorship_revenue": Decimal("0.00"),
            "is_sponsored": False,
        }
        form = StreamingSessionForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_invalid_peak_less_than_ccv(self):
        creator = CreatorFactory()
        data = {
            "creator": creator.pk,
            "platform": PlatformType.TWITCH,
            "session_title": "Daily Stream",
            "game_or_category": "Minecraft",
            "streamed_at": timezone.now(),
            "avg_ccv": 1500,
            "peak_viewers": 500,
        }
        form = StreamingSessionForm(data=data)
        assert not form.is_valid()
        assert "peak_viewers" in form.errors

    def test_form_invalid_sponsored_without_revenue(self):
        creator = CreatorFactory()
        data = {
            "creator": creator.pk,
            "platform": PlatformType.TWITCH,
            "session_title": "Daily Stream",
            "game_or_category": "Minecraft",
            "streamed_at": timezone.now(),
            "is_sponsored": True,
            "sponsorship_revenue": Decimal("0.00"),
        }
        form = StreamingSessionForm(data=data)
        assert not form.is_valid()
        assert "sponsorship_revenue" in form.errors


class TestSessionSegmentForm:
    def test_form_valid(self):
        session = StreamingSessionFactory(duration_seconds=3600)
        data = {
            "session": session.pk,
            "game_or_category": "Fortnite",
            "start_offset_seconds": 0,
            "duration_seconds": 1800,
            "avg_ccv": 400,
            "peak_viewers": 600,
        }
        form = SessionSegmentForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_invalid_peak_less_than_ccv(self):
        session = StreamingSessionFactory(duration_seconds=3600)
        data = {
            "session": session.pk,
            "game_or_category": "Fortnite",
            "start_offset_seconds": 0,
            "duration_seconds": 1800,
            "avg_ccv": 800,
            "peak_viewers": 400,
        }
        form = SessionSegmentForm(data=data)
        assert not form.is_valid()
        assert "peak_viewers" in form.errors
