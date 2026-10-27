import django_tables2 as tables

from .models import ImportBatch


class ImportBatchTable(tables.Table):
    filename = tables.Column(linkify=True)
    total_rows = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    valid_rows = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    error_count = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    actions = tables.TemplateColumn(
        template_name="imports/includes/batch_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = ImportBatch
        template_name = "django_tables2/bootstrap5.html"
        fields = (
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
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
