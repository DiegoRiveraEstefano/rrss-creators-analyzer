from crispy_forms.helper import FormHelper
from django import forms

from .models import ExportJob


class ExportJobForm(forms.ModelForm):
    class Meta:
        model = ExportJob
        fields = [
            "report_type",
            "export_format",
            "status",
            "rows_exported",
            "file_path",
            "filter_params",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
