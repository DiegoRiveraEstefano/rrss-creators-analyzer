from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Contract


@admin.register(Contract)
class ContractAdmin(SimpleHistoryAdmin):
    list_display = (
        "contract_code",
        "creator",
        "status",
        "start_date",
        "end_date",
        "base_monthly_retainer",
        "stream_creator_split_pct",
        "min_monthly_stream_hours",
    )
    list_filter = ("status", "auto_renew", "start_date")
    search_fields = ("contract_code", "creator__display_name", "creator__handle")
