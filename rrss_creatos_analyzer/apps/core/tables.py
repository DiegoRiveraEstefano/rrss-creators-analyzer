import django_tables2 as tables

from .models import CompanySettings


class CompanySettingsTable(tables.Table):
    company_name = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="core/includes/actions_column.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = CompanySettings
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "company_name",
            "legal_name",
            "tax_id",
            "default_currency",
            "default_timezone",
            "default_agency_split_pct",
            "default_creator_split_pct",
            "updated_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
