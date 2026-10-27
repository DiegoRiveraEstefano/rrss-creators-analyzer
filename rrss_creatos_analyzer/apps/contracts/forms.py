from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms

from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            "creator",
            "contract_code",
            "status",
            "start_date",
            "end_date",
            "auto_renew",
            "base_monthly_retainer",
            "stream_creator_split_pct",
            "stream_agency_split_pct",
            "video_creator_split_pct",
            "video_agency_split_pct",
            "sponsorship_creator_split_pct",
            "sponsorship_agency_split_pct",
            "min_monthly_stream_hours",
            "min_monthly_videos",
            "min_monthly_shorts",
            "document_url",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("creator", css_class="col-md-4"),
                Column("contract_code", css_class="col-md-4"),
                Column("status", css_class="col-md-4"),
            ),
            Row(
                Column("start_date", css_class="col-md-4"),
                Column("end_date", css_class="col-md-4"),
                Column("base_monthly_retainer", css_class="col-md-4"),
            ),
            Row(
                Column("stream_creator_split_pct", css_class="col-md-6"),
                Column("stream_agency_split_pct", css_class="col-md-6"),
            ),
            Row(
                Column("video_creator_split_pct", css_class="col-md-6"),
                Column("video_agency_split_pct", css_class="col-md-6"),
            ),
            Row(
                Column("sponsorship_creator_split_pct", css_class="col-md-6"),
                Column("sponsorship_agency_split_pct", css_class="col-md-6"),
            ),
            Row(
                Column("min_monthly_stream_hours", css_class="col-md-4"),
                Column("min_monthly_videos", css_class="col-md-4"),
                Column("min_monthly_shorts", css_class="col-md-4"),
            ),
            "auto_renew",
            "document_url",
            "notes",
        )
