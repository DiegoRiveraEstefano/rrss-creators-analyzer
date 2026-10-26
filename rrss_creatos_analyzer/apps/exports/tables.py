import django_tables2 as tables

from .models import ExportJob


class ExportJobTable(tables.Table):
    report_type = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="exports/includes/export_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = ExportJob
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "report_type",
            "export_format",
            "status",
            "rows_exported",
            "requested_by",
            "created_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
