from crispy_forms.helper import FormHelper
from django import forms

from .models import CampaignDeliverable
from .models import SponsorCampaign


class SponsorCampaignForm(forms.ModelForm):
    class Meta:
        model = SponsorCampaign
        fields = [
            "account_manager",
            "brand_name",
            "campaign_name",
            "campaign_code",
            "status",
            "start_date",
            "end_date",
            "total_budget",
            "agency_fee_amount",
            "creator_pool_amount",
            "target_views_or_impressions",
            "brief_url",
            "tags",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class CampaignDeliverableForm(forms.ModelForm):
    class Meta:
        model = CampaignDeliverable
        fields = [
            "campaign",
            "creator",
            "deliverable_type",
            "platform",
            "title",
            "due_date",
            "completed_at",
            "status",
            "agreed_creator_payout",
            "linked_session",
            "linked_publication",
            "tracking_link",
            "promo_code",
            "conversions_count",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
