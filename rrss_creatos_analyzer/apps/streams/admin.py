from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import SessionSegment
from .models import StreamingSession


class SessionSegmentInline(admin.TabularInline):
    model = SessionSegment
    extra = 0


@admin.register(StreamingSession)
class StreamingSessionAdmin(SimpleHistoryAdmin):
    list_display = (
        "session_title",
        "creator",
        "platform",
        "game_or_category",
        "streamed_at",
        "hours_streamed",
        "avg_ccv",
        "peak_viewers",
        "total_earnings",
    )
    list_filter = ("platform", "is_sponsored", "streamed_at")
    search_fields = (
        "session_title",
        "game_or_category",
        "creator__display_name",
        "creator__handle",
    )
    inlines = [SessionSegmentInline]


@admin.register(SessionSegment)
class SessionSegmentAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "game_or_category",
        "start_offset_seconds",
        "duration_seconds",
        "avg_ccv",
        "peak_viewers",
    )
    search_fields = ("session__session_title", "game_or_category")
