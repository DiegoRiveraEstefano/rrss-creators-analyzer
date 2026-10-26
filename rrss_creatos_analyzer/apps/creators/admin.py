from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator
from .models import CreatorPersonalInfo


class ChannelInline(admin.TabularInline):
    model = Channel
    extra = 0


class CreatorPersonalInfoInline(admin.StackedInline):
    model = CreatorPersonalInfo
    can_delete = False
    extra = 0


@admin.register(Creator)
class CreatorAdmin(SimpleHistoryAdmin):
    list_display = (
        "display_name",
        "handle",
        "get_primary_platform",
        "tier",
        "status",
        "manager",
        "joined_company_at",
    )
    list_filter = ("tier", "status", "channels__platform")
    search_fields = (
        "display_name",
        "handle",
        "personal_info__legal_full_name",
        "personal_info__contact_email",
    )
    prepopulated_fields = {"slug": ("handle",)}
    inlines = [CreatorPersonalInfoInline, ChannelInline]

    @admin.display(description="Plataforma Principal")
    def get_primary_platform(self, obj):
        return obj.get_primary_platform_display


@admin.register(CreatorPersonalInfo)
class CreatorPersonalInfoAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "legal_full_name",
        "tax_id",
        "contact_email",
        "phone_number",
        "country_code",
    )
    search_fields = (
        "creator__display_name",
        "creator__handle",
        "legal_full_name",
        "tax_id",
        "contact_email",
    )
    list_filter = ("country_code",)


@admin.register(Channel)
class ChannelAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "platform",
        "platform_channel_id",
        "is_primary",
        "followers_count",
        "subscribers_count",
        "is_live",
        "status",
    )
    list_filter = ("platform", "is_primary", "status", "is_live", "is_monetized")
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
