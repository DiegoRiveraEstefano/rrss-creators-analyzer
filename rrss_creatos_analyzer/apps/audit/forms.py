from crispy_forms.helper import FormHelper
from django import forms

from .models import AuditEvent


class AuditEventForm(forms.ModelForm):
    class Meta:
        model = AuditEvent
        fields = [
            "actor",
            "event_action",
            "target_model",
            "target_object_id",
            "ip_address",
            "summary",
            "changes_payload",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
