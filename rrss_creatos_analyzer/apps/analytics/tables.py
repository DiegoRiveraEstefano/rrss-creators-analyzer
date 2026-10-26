import django_tables2 as tables

from .models import AnalyticsSnapshot


class AnalyticsSnapshotTable(tables.Table):
    cache_key = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="analytics/includes/snapshot_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = AnalyticsSnapshot
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "cache_key",
            "report_type",
            "period_label",
            "records_count",
            "expires_at",
            "updated_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
