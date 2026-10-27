from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import CreatorPayout


@admin.register(CreatorPayout)
class CreatorPayoutAdmin(SimpleHistoryAdmin):
    list_display = (
        "creator",
        "period_year",
        "period_month",
        "status",
        "gross_stream_revenue",
        "gross_video_revenue",
        "agency_commission_amount",
        "net_creator_payout",
        "paid_at",
    )
    list_filter = ("status", "period_year", "period_month")
    search_fields = ("creator__display_name", "invoice_reference")
