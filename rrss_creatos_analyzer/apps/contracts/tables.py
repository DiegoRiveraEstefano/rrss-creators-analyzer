import django_tables2 as tables

from .models import Contract


class ContractTable(tables.Table):
    contract_code = tables.Column(linkify=True)
    base_monthly_retainer = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    min_monthly_stream_hours = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="contracts/includes/contract_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = Contract
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "contract_code",
            "creator",
            "status",
            "start_date",
            "end_date",
            "base_monthly_retainer",
            "stream_creator_split_pct",
            "min_monthly_stream_hours",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
