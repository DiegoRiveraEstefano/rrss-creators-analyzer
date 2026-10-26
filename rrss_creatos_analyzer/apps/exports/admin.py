from django.contrib import admin

from .models import ExportJob


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = (
        "report_type",
        "export_format",
        "status",
        "rows_exported",
        "requested_by",
        "created_at",
    )
    list_filter = ("report_type", "export_format", "status")
