from crispy_forms.helper import FormHelper
from django import forms

from .models import ChannelAlert


class ChannelAlertForm(forms.ModelForm):
    class Meta:
        model = ChannelAlert
        fields = [
            "creator",
            "channel",
            "alert_type",
            "severity",
            "status",
            "title",
            "occurred_at",
            "strike_points",
            "strike_expires_at",
            "account_suspension_days",
            "related_session",
            "related_publication",
            "assigned_to",
            "resolved_by",
            "resolved_at",
            "evidence_url",
            "description",
            "resolution_notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
