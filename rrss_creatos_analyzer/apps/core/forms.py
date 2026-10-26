from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from django import forms

from .models import CompanySettings


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = [
            "company_name",
            "legal_name",
            "tax_id",
            "logo_url",
            "default_currency",
            "default_timezone",
            "default_agency_split_pct",
            "default_creator_split_pct",
            "alert_webhook_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("company_name", css_class="col-md-6"),
                Column("legal_name", css_class="col-md-6"),
            ),
            Row(
                Column("tax_id", css_class="col-md-4"),
                Column("default_currency", css_class="col-md-4"),
                Column("default_timezone", css_class="col-md-4"),
            ),
            Row(
                Column("default_agency_split_pct", css_class="col-md-6"),
                Column("default_creator_split_pct", css_class="col-md-6"),
            ),
            Row(
                Column("logo_url", css_class="col-md-6"),
                Column("alert_webhook_url", css_class="col-md-6"),
            ),
        )
