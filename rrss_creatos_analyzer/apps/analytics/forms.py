from crispy_forms.helper import FormHelper
from django import forms

from .models import AnalyticsSnapshot


class AnalyticsSnapshotForm(forms.ModelForm):
    class Meta:
        model = AnalyticsSnapshot
        fields = [
            "cache_key",
            "report_type",
            "period_label",
            "records_count",
            "expires_at",
            "payload",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
