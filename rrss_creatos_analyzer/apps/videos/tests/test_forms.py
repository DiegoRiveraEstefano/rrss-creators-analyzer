from decimal import Decimal

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import PublicationType
from rrss_creatos_analyzer.apps.core.choices import VideoFormat
from rrss_creatos_analyzer.apps.core.choices import VideoRelationType
from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.videos.forms import VideoForm
from rrss_creatos_analyzer.apps.videos.forms import VideoPublicationForm
from rrss_creatos_analyzer.apps.videos.forms import VideoRelationForm

from .factories import VideoFactory

pytestmark = pytest.mark.django_db


class TestVideoForm:
    def test_form_valid(self):
        creator = CreatorFactory()
        data = {
            "creator": creator.pk,
            "title": "My New Project",
            "category": "Tech",
            "content_format": VideoFormat.LONG_FORM,
            "status": VideoStatus.IDEA,
            "duration_seconds": 600,
            "production_cost": Decimal("50.00"),
            "editing_cost": Decimal("50.00"),
            "thumbnail_cost": Decimal("20.00"),
        }
        form = VideoForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_invalid_published_without_publication(self):
        creator = CreatorFactory()
        data = {
            "creator": creator.pk,
            "title": "My New Project",
            "category": "Tech",
            "content_format": VideoFormat.LONG_FORM,
            "status": VideoStatus.PUBLISHED,
        }
        form = VideoForm(data=data)
        assert not form.is_valid()
        assert "status" in form.errors


class TestVideoPublicationForm:
    def test_form_valid(self):
        video = VideoFactory()
        channel = ChannelFactory(creator=video.creator)
        data = {
            "video": video.pk,
            "creator": video.creator.pk,
            "channel": channel.pk,
            "platform": PlatformType.YOUTUBE,
            "publication_type": PublicationType.STANDARD,
            "status": PublicationStatus.PUBLISHED,
            "published_at": timezone.now(),
            "published_title": "Uploaded Video",
            "views_count": 1000,
            "unique_viewers_count": 800,
            "impressions_count": 5000,
            "click_through_rate": Decimal("5.00"),
            "likes_count": 100,
            "dislikes_count": 2,
            "comments_count": 20,
            "shares_count": 10,
            "saves_count": 5,
            "watch_time_hours": Decimal("50.00"),
            "avg_view_duration_seconds": 180,
            "retention_rate_pct": Decimal("40.00"),
            "engagement_rate": Decimal("13.50"),
            "ad_revenue": Decimal("10.00"),
            "sponsorship_revenue": Decimal("0.00"),
            "estimated_revenue": Decimal("10.00"),
        }
        form = VideoPublicationForm(data=data)
        assert form.is_valid(), form.errors


class TestVideoRelationForm:
    def test_form_valid(self):
        v1 = VideoFactory()
        v2 = VideoFactory()
        data = {
            "source_video": v1.pk,
            "target_video": v2.pk,
            "relation_type": VideoRelationType.CLIP,
        }
        form = VideoRelationForm(data=data)
        assert form.is_valid(), form.errors

    def test_form_invalid_self_relation(self):
        v1 = VideoFactory()
        data = {
            "source_video": v1.pk,
            "target_video": v1.pk,
            "relation_type": VideoRelationType.CLIP,
        }
        form = VideoRelationForm(data=data)
        assert not form.is_valid()
        assert "target_video" in form.errors
