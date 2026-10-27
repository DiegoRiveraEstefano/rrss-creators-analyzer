from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException


@admin.register(CreatorSchedulePattern)
class CreatorSchedulePatternAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "title",
        "start_time",
        "end_time",
        "platform",
        "planned_duration_minutes",
        "is_mandatory",
        "is_active",
        "effective_from",
    )
    list_filter = ("platform", "is_mandatory", "is_active")
    search_fields = (
        "creator__display_name",
        "creator__handle",
        "title",
        "rrule",
        "category_or_game",
    )
    raw_id_fields = ("creator", "channel")


@admin.register(CreatorScheduleSlot)
class CreatorScheduleSlotAdmin(SimpleHistoryAdmin):
    list_display = (
        "scheduled_date",
        "creator",
        "scheduled_start_time",
        "planned_hours",
        "actual_hours",
        "compliance_rate_pct",
        "start_delay_minutes",
        "status",
        "is_mandatory",
    )
    list_filter = ("status", "is_mandatory", "scheduled_date")
    search_fields = ("creator__display_name", "title", "category_or_game")
    raw_id_fields = (
        "creator",
        "channel",
        "schedule_pattern",
        "actual_streaming_session",
    )
    date_hierarchy = "scheduled_date"


@admin.register(ScheduleException)
class ScheduleExceptionAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "start_date",
        "end_date",
        "reason_type",
        "title",
        "is_approved",
        "approved_by",
    )
    list_filter = ("reason_type", "is_approved", "start_date")
    search_fields = ("creator__display_name", "title", "description")
    raw_id_fields = ("creator", "approved_by")


@admin.register(CreatorScheduleComplianceSummary)
class CreatorScheduleComplianceSummaryAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "year",
        "month",
        "stipulated_days_count",
        "completed_days_count",
        "days_compliance_rate_pct",
        "hours_compliance_rate_pct",
        "punctuality_rate_pct",
        "is_compliant",
    )
    list_filter = ("year", "month", "is_compliant")
    search_fields = ("creator__display_name", "audit_notes")
    raw_id_fields = ("creator",)
