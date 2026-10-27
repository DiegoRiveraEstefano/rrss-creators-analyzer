from crispy_forms.helper import FormHelper
from django import forms

from .models import EditingTask
from .models import Editor
from .models import EditorAssignment
from .models import TaskRevision


class EditorForm(forms.ModelForm):
    class Meta:
        model = Editor
        fields = [
            "name",
            "handle",
            "slug",
            "user",
            "status",
            "editor_type",
            "primary_specialty",
            "software_stack",
            "rate_model",
            "base_video_rate",
            "base_short_rate",
            "hourly_rate",
            "monthly_retainer",
            "max_active_tasks",
            "email",
            "phone",
            "discord_handle",
            "portfolio_url",
            "reel_url",
            "tags",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class EditorAssignmentForm(forms.ModelForm):
    class Meta:
        model = EditorAssignment
        fields = [
            "editor",
            "creator",
            "role",
            "status",
            "is_primary",
            "agreed_video_rate",
            "agreed_short_rate",
            "start_date",
            "end_date",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class EditingTaskForm(forms.ModelForm):
    class Meta:
        model = EditingTask
        fields = [
            "title",
            "creator",
            "editor",
            "video",
            "status",
            "priority",
            "task_type",
            "assigned_date",
            "deadline",
            "agreed_cost",
            "brief",
            "raw_footage_url",
            "preview_render_url",
            "final_render_url",
            "is_paid",
            "tags",
        ]
        widgets = {
            "assigned_date": forms.DateInput(attrs={"type": "date"}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class TaskRevisionForm(forms.ModelForm):
    class Meta:
        model = TaskRevision
        fields = [
            "task",
            "revision_number",
            "render_url",
            "change_summary",
            "feedback_notes",
            "status",
            "submitted_at",
            "reviewed_at",
        ]
        widgets = {
            "submitted_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reviewed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
