from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import ImportBatch


@admin.register(ImportBatch)
class ImportBatchAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "filename",
        "batch_type",
        "source_platform",
        "total_rows",
        "valid_rows",
        "error_count",
        "status",
        "uploaded_by",
        "created_at",
    )
    list_filter = ("batch_type", "source_platform", "status")
    search_fields = ("filename", "file_hash_sha256")
