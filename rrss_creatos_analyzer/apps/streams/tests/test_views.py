import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

from .factories import SessionSegmentFactory
from .factories import StreamingSessionFactory

pytestmark = pytest.mark.django_db


class TestStreamingSessionViews:
    def test_session_list_view_authenticated(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        session = StreamingSessionFactory()

        response = client.get(reverse("streams:session_list"))
        assert response.status_code == 200  # noqa: PLR2004
        assert session.session_title.encode() in response.content

    def test_session_detail_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        session = StreamingSessionFactory()

        response = client.get(
            reverse("streams:session_detail", kwargs={"pk": session.pk}),
        )
        assert response.status_code == 200  # noqa: PLR2004

    def test_category_performance_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        StreamingSessionFactory(game_or_category="Apex Legends")

        response = client.get(reverse("streams:category_performance"))
        assert response.status_code == 200  # noqa: PLR2004
        assert b"Apex Legends" in response.content

    def test_segment_detail_view(self, client):
        user = UserFactory(is_superuser=True)
        client.force_login(user)
        segment = SessionSegmentFactory()

        response = client.get(
            reverse("streams:segment_detail", kwargs={"pk": segment.pk}),
        )
        assert response.status_code == 200  # noqa: PLR2004
