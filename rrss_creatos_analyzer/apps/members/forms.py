from crispy_forms.helper import FormHelper
from django import forms

from .models import CreatorTeamAssignment
from .models import MemberInvitation


class MemberInvitationForm(forms.ModelForm):
    class Meta:
        model = MemberInvitation
        fields = ["email", "full_name", "target_group", "status", "expires_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class CreatorTeamAssignmentForm(forms.ModelForm):
    class Meta:
        model = CreatorTeamAssignment
        fields = ["creator", "user", "group", "responsibility", "is_primary"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
