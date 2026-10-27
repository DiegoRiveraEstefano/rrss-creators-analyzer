from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Video
from .models import VideoPublication
from .models import VideoRelation


class VideoPublicationInline(admin.TabularInline):
    model = VideoPublication
    extra = 0


@admin.register(Video)
class VideoAdmin(SimpleHistoryAdmin):
    list_display = (
        "title",
        "creator",
        "category",
        "content_format",
        "duration_seconds",
        "total_production_cost",
        "status",
        "created_at",
    )
    list_filter = ("status", "content_format", "category")
    search_fields = ("title", "internal_code", "internal_name", "creator__display_name")
    inlines = [VideoPublicationInline]


@admin.register(VideoPublication)
class VideoPublicationAdmin(SimpleHistoryAdmin):
    list_display = (
        "video",
        "creator",
        "platform",
        "publication_type",
        "published_at",
        "views_count",
        "likes_count",
        "estimated_revenue",
        "rpm_estimated",
    )
    list_filter = ("platform", "publication_type", "status")
    search_fields = (
        "video__title",
        "published_title",
        "platform_post_id",
        "creator__display_name",
    )


@admin.register(VideoRelation)
class VideoRelationAdmin(admin.ModelAdmin):
    list_display = (
        "source_video",
        "relation_type",
        "target_video",
        "target_session",
        "created_at",
    )
    list_filter = ("relation_type",)
    search_fields = ("source_video__title", "description")
