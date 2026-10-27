from crispy_forms.helper import FormHelper
from django import forms

from .models import CreatorPayout


class CreatorPayoutForm(forms.ModelForm):
    class Meta:
        model = CreatorPayout
        fields = [
            "creator",
            "contract",
            "period_year",
            "period_month",
            "status",
            "gross_stream_revenue",
            "gross_video_revenue",
            "gross_sponsorship_revenue",
            "base_retainer_amount",
            "bonuses_amount",
            "deductions_or_recoupment",
            "agency_commission_amount",
            "net_creator_payout",
            "invoice_reference",
            "approved_by",
            "paid_at",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
