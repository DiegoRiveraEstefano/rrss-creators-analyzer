from decimal import Decimal

import pytest

from rrss_creatos_analyzer.apps.core.choices import VideoFormat
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory
from rrss_creatos_analyzer.apps.videos.selectors import VideoPublicationSelector
from rrss_creatos_analyzer.apps.videos.selectors import VideoRelationSelector
from rrss_creatos_analyzer.apps.videos.selectors import VideoSelector

from .factories import VideoFactory
from .factories import VideoPublicationFactory
from .factories import VideoRelationFactory

pytestmark = pytest.mark.django_db


class TestVideoSelector:
    def test_get_visible_queryset_for_creator_user(self):
        user = UserFactory()
        creator = CreatorFactory(user=user)
        video = VideoFactory(creator=creator)
        other_video = VideoFactory()

        qs = VideoSelector.get_visible_queryset(user=user)
        assert video in qs
        assert other_video not in qs

    def test_get_profitability_audit(self):
        user = UserFactory(is_superuser=True)
        v1 = VideoFactory(
            total_production_cost=Decimal("100.00"),
            content_format=VideoFormat.LONG_FORM,
        )
        VideoPublicationFactory(
            video=v1,
            estimated_revenue=Decimal("150.00"),
        )
        v2 = VideoFactory(
            total_production_cost=Decimal("200.00"),
            content_format=VideoFormat.LONG_FORM,
        )
        VideoPublicationFactory(
            video=v2,
            estimated_revenue=Decimal("50.00"),
        )

        audit = VideoSelector.get_profitability_audit(
            user=user,
            content_format=VideoFormat.LONG_FORM,
        )
        assert len(audit) == 2  # noqa: PLR2004
        row1 = next(r for r in audit if r["video"].pk == v1.pk)
        row2 = next(r for r in audit if r["video"].pk == v2.pk)
        assert row1["profit_category"] == "Rentable"
        assert row2["profit_category"] == "Deficitario"


class TestVideoPublicationSelector:
    def test_get_visible_queryset_for_creator_user(self):
        user = UserFactory()
        creator = CreatorFactory(user=user)
        pub = VideoPublicationFactory(creator=creator)
        other_pub = VideoPublicationFactory()

        qs = VideoPublicationSelector.get_visible_queryset(user=user)
        assert pub in qs
        assert other_pub not in qs


class TestVideoRelationSelector:
    def test_get_visible_queryset_for_creator_user(self):
        user = UserFactory()
        creator = CreatorFactory(user=user)
        v1 = VideoFactory(creator=creator)
        v2 = VideoFactory()
        rel = VideoRelationFactory(source_video=v1, target_video=v2)
        other_rel = VideoRelationFactory()

        qs = VideoRelationSelector.get_visible_queryset(user=user)
        assert rel in qs
        assert other_rel not in qs
