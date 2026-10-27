import django_tables2 as tables

from .models import CampaignDeliverable
from .models import SponsorCampaign


class SponsorCampaignTable(tables.Table):
    campaign_code = tables.Column(linkify=True)
    total_budget = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    agency_fee_amount = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    creator_pool_amount = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="campaigns/includes/campaign_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = SponsorCampaign
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "campaign_code",
            "brand_name",
            "campaign_name",
            "status",
            "start_date",
            "end_date",
            "total_budget",
            "agency_fee_amount",
            "creator_pool_amount",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class CampaignDeliverableTable(tables.Table):
    title = tables.Column(linkify=True)
    agreed_creator_payout = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    conversions_count = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="campaigns/includes/deliverable_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = CampaignDeliverable
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "title",
            "campaign",
            "creator",
            "deliverable_type",
            "platform",
            "due_date",
            "status",
            "agreed_creator_payout",
            "conversions_count",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
