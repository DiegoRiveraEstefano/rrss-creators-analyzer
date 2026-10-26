import django_tables2 as tables

from .models import AuditEvent


class AuditEventTable(tables.Table):
    created_at = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="audit/includes/audit_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = AuditEvent
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "created_at",
            "actor",
            "event_action",
            "target_model",
            "target_object_id",
            "ip_address",
            "summary",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
