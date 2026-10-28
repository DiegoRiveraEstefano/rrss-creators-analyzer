import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

from .factories import VideoFactory
from .factories import VideoPublicationFactory
from .factories import VideoRelationFactory

pytestmark = pytest.mark.django_db


class TestVideoViews:
    def test_video_list_view_authenticated(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        video = VideoFactory()

        response = client.get(reverse("videos:video_list"))
        assert response.status_code == 200  # noqa: PLR2004
        assert video.title.encode() in response.content

    def test_video_detail_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        video = VideoFactory()

        response = client.get(
            reverse("videos:video_detail", kwargs={"pk": video.pk}),
        )
        assert response.status_code == 200  # noqa: PLR2004

    def test_profitability_audit_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        VideoFactory(title="Profit Video")

        response = client.get(reverse("videos:profitability_audit"))
        assert response.status_code == 200  # noqa: PLR2004
        assert b"Profit Video" in response.content

    def test_publication_detail_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        pub = VideoPublicationFactory()

        response = client.get(
            reverse("videos:publication_detail", kwargs={"pk": pub.pk}),
        )
        assert response.status_code == 200  # noqa: PLR2004

    def test_relation_detail_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        rel = VideoRelationFactory()

        response = client.get(
            reverse("videos:relation_detail", kwargs={"pk": rel.pk}),
        )
        assert response.status_code == 200  # noqa: PLR2004
