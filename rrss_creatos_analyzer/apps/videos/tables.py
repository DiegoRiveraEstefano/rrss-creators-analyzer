import django_tables2 as tables

from .models import Video
from .models import VideoPublication
from .models import VideoRelation


class VideoTable(tables.Table):
    title = tables.Column(linkify=True)
    duration_seconds = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    total_production_cost = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="videos/includes/video_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = Video
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "title",
            "creator",
            "category",
            "content_format",
            "duration_seconds",
            "total_production_cost",
            "status",
            "created_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class VideoPublicationTable(tables.Table):
    video = tables.Column(linkify=True)
    views_count = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    likes_count = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    engagement_rate = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    estimated_revenue = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    rpm_estimated = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    actions = tables.TemplateColumn(
        template_name="videos/includes/publication_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = VideoPublication
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "published_at",
            "video",
            "creator",
            "platform",
            "publication_type",
            "views_count",
            "likes_count",
            "engagement_rate",
            "estimated_revenue",
            "rpm_estimated",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class VideoRelationTable(tables.Table):
    source_video = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="videos/includes/relation_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = VideoRelation
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "source_video",
            "relation_type",
            "target_video",
            "target_session",
            "timestamp_start_seconds",
            "timestamp_end_seconds",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
