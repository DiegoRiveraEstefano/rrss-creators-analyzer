import django_tables2 as tables

from .models import CreatorPayout


class CreatorPayoutTable(tables.Table):
    creator = tables.Column(linkify=True)
    gross_stream_revenue = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    gross_video_revenue = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    agency_commission_amount = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    net_creator_payout = tables.Column(
        attrs={"td": {"class": "text-end font-monospace fw-bold"}},
    )
    actions = tables.TemplateColumn(
        template_name="payouts/includes/payout_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = CreatorPayout
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "creator",
            "period_year",
            "period_month",
            "status",
            "gross_stream_revenue",
            "gross_video_revenue",
            "agency_commission_amount",
            "net_creator_payout",
            "paid_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
