from django.urls import reverse

from .factories import VideoFactory
from .factories import VideoPublicationFactory
from .factories import VideoRelationFactory


class TestVideoURLs:
    def test_video_list_url(self):
        assert reverse("videos:video_list") == "/videos/"

    def test_video_create_url(self):
        assert reverse("videos:video_create") == "/videos/create/"

    def test_profitability_audit_url(self):
        assert reverse("videos:profitability_audit") == "/videos/profitability-audit/"

    def test_video_detail_url(self):
        video = VideoFactory.build(pk=1)
        assert reverse("videos:video_detail", kwargs={"pk": video.pk}) == "/videos/1/"

    def test_publication_detail_url(self):
        pub = VideoPublicationFactory.build(pk=3)
        assert (
            reverse("videos:publication_detail", kwargs={"pk": pub.pk})
            == "/videos/publications/3/"
        )

    def test_relation_detail_url(self):
        rel = VideoRelationFactory.build(pk=7)
        assert (
            reverse("videos:relation_detail", kwargs={"pk": rel.pk})
            == "/videos/relations/7/"
        )
