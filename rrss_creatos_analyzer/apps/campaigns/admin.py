from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import CampaignDeliverable
from .models import SponsorCampaign


class CampaignDeliverableInline(admin.TabularInline):
    model = CampaignDeliverable
    extra = 0


@admin.register(SponsorCampaign)
class SponsorCampaignAdmin(SimpleHistoryAdmin):
    list_display = (
        "campaign_code",
        "brand_name",
        "campaign_name",
        "status",
        "start_date",
        "end_date",
        "total_budget",
        "agency_fee_amount",
    )
    list_filter = ("status", "start_date")
    search_fields = ("campaign_code", "brand_name", "campaign_name")
    inlines = [CampaignDeliverableInline]


@admin.register(CampaignDeliverable)
class CampaignDeliverableAdmin(SimpleHistoryAdmin):
    list_display = (
        "title",
        "campaign",
        "creator",
        "deliverable_type",
        "platform",
        "status",
        "due_date",
        "agreed_creator_payout",
    )
    list_filter = ("status", "deliverable_type", "platform")
    search_fields = (
        "title",
        "campaign__brand_name",
        "creator__display_name",
        "promo_code",
    )
