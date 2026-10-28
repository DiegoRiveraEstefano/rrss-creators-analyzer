from django.urls import reverse

from .factories import SessionSegmentFactory
from .factories import StreamingSessionFactory


class TestStreamingSessionURLs:
    def test_session_list_url(self):
        assert reverse("streams:session_list") == "/streams/"

    def test_session_create_url(self):
        assert reverse("streams:session_create") == "/streams/create/"

    def test_category_performance_url(self):
        assert (
            reverse("streams:category_performance") == "/streams/category-performance/"
        )

    def test_session_detail_url(self):
        session = StreamingSessionFactory.build(pk=1)
        assert (
            reverse("streams:session_detail", kwargs={"pk": session.pk})
            == "/streams/1/"
        )

    def test_segment_detail_url(self):
        segment = SessionSegmentFactory.build(pk=5)
        assert (
            reverse("streams:segment_detail", kwargs={"pk": segment.pk})
            == "/streams/segments/5/"
        )
