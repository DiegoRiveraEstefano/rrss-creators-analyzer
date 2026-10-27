from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import CompanySettings


@admin.register(CompanySettings)
class CompanySettingsAdmin(SimpleHistoryAdmin):
    list_display = (
        "company_name",
        "legal_name",
        "default_currency",
        "default_timezone",
        "default_agency_split_pct",
        "default_creator_split_pct",
        "updated_at",
    )
    search_fields = ("company_name", "legal_name", "tax_id")
