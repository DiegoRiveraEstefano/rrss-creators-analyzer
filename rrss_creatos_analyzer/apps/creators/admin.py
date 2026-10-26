from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator


class ChannelInline(admin.TabularInline):
    model = Channel
    extra = 0


@admin.register(Creator)
class CreatorAdmin(SimpleHistoryAdmin):
    list_display = (
        "display_name",
        "handle",
        "primary_platform",
        "tier",
        "status",
        "manager",
        "joined_company_at",
    )
    list_filter = ("primary_platform", "tier", "status")
    search_fields = ("display_name", "handle", "legal_full_name", "contact_email")
    prepopulated_fields = {"slug": ("handle",)}
    inlines = [ChannelInline]


@admin.register(Channel)
class ChannelAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "platform",
        "platform_channel_id",
        "followers_count",
        "subscribers_count",
        "is_live",
        "status",
    )
    list_filter = ("platform", "status", "is_live", "is_monetized")
    search_fields = ("creator__display_name", "handle", "platform_channel_id")


@admin.register(ChannelSnapshot)
class ChannelSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "channel",
        "snapshot_date",
        "followers_count",
        "followers_delta",
        "subscribers_count",
        "total_views_count",
    )
    list_filter = ("snapshot_date", "channel__platform")
    search_fields = ("channel__creator__display_name", "channel__handle")
