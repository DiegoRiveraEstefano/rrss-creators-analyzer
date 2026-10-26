from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import ChannelAlert


@admin.register(ChannelAlert)
class ChannelAlertAdmin(SimpleHistoryAdmin):
    list_display = (
        "title",
        "creator",
        "channel",
        "alert_type",
        "severity",
        "status",
        "strike_points",
        "occurred_at",
    )
    list_filter = ("severity", "status", "alert_type")
    search_fields = ("title", "description", "creator__display_name", "creator__handle")
