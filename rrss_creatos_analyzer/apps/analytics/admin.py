from django.contrib import admin

from .models import AnalyticsSnapshot


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "cache_key",
        "report_type",
        "period_label",
        "records_count",
        "expires_at",
        "updated_at",
    )
    list_filter = ("report_type", "period_label")
