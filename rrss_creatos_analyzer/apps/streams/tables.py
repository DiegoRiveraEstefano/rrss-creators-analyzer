import django_tables2 as tables

from .models import SessionSegment
from .models import StreamingSession


class StreamingSessionTable(tables.Table):
    session_title = tables.Column(linkify=True)
    hours_streamed = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    avg_ccv = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    peak_viewers = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    total_earnings = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    earnings_per_hour = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="streams/includes/session_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = StreamingSession
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "streamed_at",
            "creator",
            "platform",
            "session_title",
            "game_or_category",
            "hours_streamed",
            "avg_ccv",
            "peak_viewers",
            "total_earnings",
            "earnings_per_hour",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class SessionSegmentTable(tables.Table):
    game_or_category = tables.Column(linkify=True)
    duration_seconds = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    avg_ccv = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    peak_viewers = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    actions = tables.TemplateColumn(
        template_name="streams/includes/segment_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = SessionSegment
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "session",
            "game_or_category",
            "start_offset_seconds",
            "duration_seconds",
            "avg_ccv",
            "peak_viewers",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
