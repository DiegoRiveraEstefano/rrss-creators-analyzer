from decimal import Decimal

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.campaigns.models import CampaignDeliverable
from rrss_creatos_analyzer.apps.campaigns.models import SponsorCampaign
from rrss_creatos_analyzer.apps.core.choices import DeliverableStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import VideoRelationType
from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.streams.tests.factories import StreamingSessionFactory
from rrss_creatos_analyzer.apps.videos.models import Video
from rrss_creatos_analyzer.apps.videos.models import VideoPublication
from rrss_creatos_analyzer.apps.videos.models import VideoRelation
from rrss_creatos_analyzer.apps.videos.services import VideoPublicationService
from rrss_creatos_analyzer.apps.videos.services import VideoRelationService
from rrss_creatos_analyzer.apps.videos.services import VideoService

from .factories import VideoFactory
from .factories import VideoPublicationFactory
from .factories import VideoRelationFactory

pytestmark = pytest.mark.django_db


class TestVideoService:
    def test_save_video_calculates_costs(self):
        creator = CreatorFactory()
        video = VideoService.save_video(
            creator=creator,
            title="Minecraft Survival Ep 1",
            production_cost=Decimal("120.00"),
            editing_cost=Decimal("80.00"),
            thumbnail_cost=Decimal("30.00"),
        )
        assert video.pk is not None
        assert video.total_production_cost == Decimal("230.00")

    def test_save_video_negative_cost_raises_error(self):
        creator = CreatorFactory()
        with pytest.raises(BusinessLogicError, match="no pueden ser negativos"):
            VideoService.save_video(
                creator=creator,
                title="Bad Cost Video",
                production_cost=Decimal("-10.00"),
            )

    def test_save_video_published_without_publication_raises_error(self):
        creator = CreatorFactory()
        with pytest.raises(BusinessLogicError, match="sin publicaciones vinculadas"):
            VideoService.save_video(
                creator=creator,
                title="Instant Published",
                status=VideoStatus.PUBLISHED,
            )

    def test_save_video_update_published_requires_published_publication(self):
        video = VideoFactory(status=VideoStatus.READY)
        with pytest.raises(BusinessLogicError, match="al menos una publicación"):
            VideoService.save_video(
                instance=video,
                status=VideoStatus.PUBLISHED,
            )

    def test_delete_video(self):
        video = VideoFactory()
        VideoService.delete_video(instance=video)
        assert not Video.objects.filter(pk=video.pk).exists()


class TestVideoPublicationService:
    def test_save_publication_calculates_rpm_and_engagement(self):
        video = VideoFactory()
        pub = VideoPublicationService.save_publication(
            video=video,
            creator=video.creator,
            platform=PlatformType.YOUTUBE,
            published_at=timezone.now(),
            views_count=20000,
            likes_count=1000,
            comments_count=200,
            shares_count=50,
            saves_count=50,
            ad_revenue=Decimal("80.00"),
            sponsorship_revenue=Decimal("20.00"),
        )
        assert pub.pk is not None
        assert pub.estimated_revenue == Decimal("100.00")
        assert pub.rpm_estimated == Decimal("5.00")
        # interactions = 1000 + 200 + 50 + 50 = 1300; 1300 / 20000 * 100 = 6.50%
        assert pub.engagement_rate == Decimal("6.50")

    def test_save_publication_promotes_ready_video_to_published(self):
        video = VideoFactory(status=VideoStatus.READY)
        VideoPublicationService.save_publication(
            video=video,
            creator=video.creator,
            platform=PlatformType.YOUTUBE,
            published_at=timezone.now(),
            status=PublicationStatus.PUBLISHED,
        )
        video.refresh_from_db()
        assert video.status == VideoStatus.PUBLISHED

    def test_save_publication_links_deliverable(self):
        video = VideoFactory()
        campaign = SponsorCampaign.objects.create(
            brand_name="GamerFuel",
            campaign_name="Spring Campaign",
            campaign_code="GF-02",
            start_date=timezone.localdate(),
        )
        deliverable = CampaignDeliverable.objects.create(
            campaign=campaign,
            creator=video.creator,
            title="Sponsored YouTube Video",
        )
        pub = VideoPublicationService.save_publication(
            video=video,
            creator=video.creator,
            platform=PlatformType.YOUTUBE,
            published_at=timezone.now(),
            deliverable=deliverable,
        )
        deliverable.refresh_from_db()
        assert deliverable.linked_publication == pub
        assert deliverable.status == DeliverableStatus.PUBLISHED

    def test_delete_publication(self):
        pub = VideoPublicationFactory()
        VideoPublicationService.delete_publication(instance=pub)
        assert not VideoPublication.objects.filter(pk=pub.pk).exists()


class TestVideoRelationService:
    def test_save_relation_happy_path(self):
        v1 = VideoFactory()
        v2 = VideoFactory()
        rel = VideoRelationService.save_relation(
            source_video=v1,
            target_video=v2,
            relation_type=VideoRelationType.CLIP,
        )
        assert rel.pk is not None

    def test_save_relation_with_streaming_session(self):
        video = VideoFactory()
        session = StreamingSessionFactory()
        rel = VideoRelationService.save_relation(
            source_video=video,
            target_session=session,
            relation_type=VideoRelationType.DERIVED_FROM_LIVE,
        )
        assert rel.pk is not None

    def test_save_relation_no_target_raises_error(self):
        video = VideoFactory()
        with pytest.raises(BusinessLogicError, match="al menos un Video Relacionado"):
            VideoRelationService.save_relation(source_video=video)

    def test_save_relation_self_relation_raises_error(self):
        video = VideoFactory()
        with pytest.raises(BusinessLogicError, match="consigo mismo"):
            VideoRelationService.save_relation(
                source_video=video,
                target_video=video,
            )

    def test_save_relation_duplicate_raises_error(self):
        v1 = VideoFactory()
        v2 = VideoFactory()
        VideoRelationFactory(
            source_video=v1,
            target_video=v2,
            relation_type=VideoRelationType.CLIP,
        )
        with pytest.raises(BusinessLogicError, match="Ya existe una relación"):
            VideoRelationService.save_relation(
                source_video=v1,
                target_video=v2,
                relation_type=VideoRelationType.CLIP,
            )

    def test_delete_relation(self):
        rel = VideoRelationFactory()
        VideoRelationService.delete_relation(instance=rel)
        assert not VideoRelation.objects.filter(pk=rel.pk).exists()
