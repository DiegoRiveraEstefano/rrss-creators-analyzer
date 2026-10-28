from __future__ import annotations

from decimal import Decimal

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import PublicationType
from rrss_creatos_analyzer.apps.core.choices import VideoFormat
from rrss_creatos_analyzer.apps.core.choices import VideoRelationType
from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.creators.tests.factories import ChannelFactory
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.videos.models import Video
from rrss_creatos_analyzer.apps.videos.models import VideoPublication
from rrss_creatos_analyzer.apps.videos.models import VideoRelation


class VideoFactory(DjangoModelFactory[Video]):
    creator = factory.SubFactory(CreatorFactory)
    title = factory.Sequence(lambda n: f"Video Project #{n}")
    internal_code = factory.Sequence(lambda n: f"VID-{n:04d}")
    category = "Gaming"
    content_format = VideoFormat.LONG_FORM
    status = VideoStatus.IDEA
    production_cost = Decimal("100.00")
    editing_cost = Decimal("150.00")
    thumbnail_cost = Decimal("50.00")
    total_production_cost = Decimal("300.00")

    class Meta:
        model = Video


class VideoPublicationFactory(DjangoModelFactory[VideoPublication]):
    video = factory.SubFactory(VideoFactory)
    creator = factory.LazyAttribute(lambda o: o.video.creator)
    channel = factory.SubFactory(
        ChannelFactory, creator=factory.SelfAttribute("..creator"),
    )
    platform = PlatformType.YOUTUBE
    publication_type = PublicationType.STANDARD
    status = PublicationStatus.PUBLISHED
    published_at = factory.LazyFunction(timezone.now)
    views_count = 10000
    likes_count = 500
    comments_count = 100
    shares_count = 50
    saves_count = 25
    estimated_revenue = Decimal("40.00")
    rpm_estimated = Decimal("4.00")
    engagement_rate = Decimal("6.75")

    class Meta:
        model = VideoPublication


class VideoRelationFactory(DjangoModelFactory[VideoRelation]):
    source_video = factory.SubFactory(VideoFactory)
    target_video = factory.SubFactory(VideoFactory)
    relation_type = VideoRelationType.CLIP

    class Meta:
        model = VideoRelation
