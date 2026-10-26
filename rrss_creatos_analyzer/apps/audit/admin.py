from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "actor",
        "event_action",
        "target_model",
        "target_object_id",
        "ip_address",
        "summary",
    )
    list_filter = ("event_action", "target_model", "actor")
