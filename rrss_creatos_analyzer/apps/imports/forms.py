from crispy_forms.helper import FormHelper
from django import forms

from .models import ImportBatch


class ImportBatchForm(forms.ModelForm):
    class Meta:
        model = ImportBatch
        fields = [
            "batch_type",
            "source_platform",
            "filename",
            "file_path",
            "file_hash_sha256",
            "total_rows",
            "valid_rows",
            "created_rows",
            "updated_rows",
            "skipped_rows",
            "error_count",
            "status",
            "error_summary",
            "completed_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
