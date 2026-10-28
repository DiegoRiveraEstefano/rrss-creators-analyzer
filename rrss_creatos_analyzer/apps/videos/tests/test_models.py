from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from rrss_creatos_analyzer.apps.core.choices import VideoRelationType

from .factories import VideoFactory
from .factories import VideoPublicationFactory
from .factories import VideoRelationFactory

pytestmark = pytest.mark.django_db


class TestVideoModel:
    def test_str_and_get_absolute_url(self):
        video = VideoFactory(title="Epic Minecraft Movie")
        assert "Epic Minecraft Movie" in str(video)
        assert video.get_absolute_url() == f"/videos/{video.pk}/"

    def test_net_profit_and_roi_properties(self):
        video = VideoFactory(
            production_cost=Decimal("100.00"),
            editing_cost=Decimal("100.00"),
            thumbnail_cost=Decimal("0.00"),
            total_production_cost=Decimal("200.00"),
        )
        VideoPublicationFactory(
            video=video,
            estimated_revenue=Decimal("300.00"),
        )
        assert video.net_profit == Decimal("100.00")
        assert video.roi_percentage == Decimal("50.00")

    def test_roi_when_zero_cost(self):
        video = VideoFactory(
            production_cost=Decimal("0.00"),
            editing_cost=Decimal("0.00"),
            thumbnail_cost=Decimal("0.00"),
            total_production_cost=Decimal("0.00"),
        )
        assert video.roi_percentage is None


class TestVideoPublicationModel:
    def test_str_and_get_absolute_url(self):
        pub = VideoPublicationFactory()
        assert pub.video.title in str(pub)
        assert pub.get_absolute_url() == f"/videos/publications/{pub.pk}/"

    def test_net_profit_and_roi(self):
        video = VideoFactory(total_production_cost=Decimal("100.00"))
        pub = VideoPublicationFactory(
            video=video,
            estimated_revenue=Decimal("150.00"),
        )
        assert pub.net_profit == Decimal("50.00")
        assert pub.roi_percentage == Decimal("50.00")


class TestVideoRelationModel:
    def test_str_and_get_absolute_url(self):
        rel = VideoRelationFactory()
        assert rel.source_video.title in str(rel)
        assert rel.get_absolute_url() == f"/videos/relations/{rel.pk}/"

    def test_clean_self_relation_raises_error(self):
        video = VideoFactory()
        rel = VideoRelationFactory.build(
            source_video=video,
            target_video=video,
        )
        with pytest.raises(ValidationError):
            rel.clean()

    def test_clean_no_target_raises_error(self):
        video = VideoFactory()
        rel = VideoRelationFactory.build(
            source_video=video,
            target_video=None,
            target_session=None,
        )
        with pytest.raises(ValidationError):
            rel.clean()

    def test_clean_invalid_timestamps_raises_error(self):
        rel = VideoRelationFactory.build(
            timestamp_start_seconds=100,
            timestamp_end_seconds=50,
        )
        with pytest.raises(ValidationError):
            rel.clean()

    def test_duplicate_relation_raises_integrity_error(self):
        v1 = VideoFactory()
        v2 = VideoFactory()
        VideoRelationFactory(
            source_video=v1,
            target_video=v2,
            relation_type=VideoRelationType.CLIP,
        )
        with pytest.raises(IntegrityError):
            VideoRelationFactory(
                source_video=v1,
                target_video=v2,
                relation_type=VideoRelationType.CLIP,
            )
