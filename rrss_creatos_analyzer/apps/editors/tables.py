import django_tables2 as tables

from .models import EditingTask
from .models import Editor
from .models import EditorAssignment
from .models import TaskRevision


class EditorTable(tables.Table):
    name = tables.Column(linkify=True)
    base_video_rate = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    base_short_rate = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    hourly_rate = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    actions = tables.TemplateColumn(
        template_name="editors/includes/editor_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = Editor
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "name",
            "handle",
            "status",
            "editor_type",
            "primary_specialty",
            "rate_model",
            "base_video_rate",
            "base_short_rate",
            "hourly_rate",
            "max_active_tasks",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class EditorAssignmentTable(tables.Table):
    editor = tables.Column(linkify=True)
    creator = tables.Column(linkify=True)
    agreed_video_rate = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    agreed_short_rate = tables.Column(
        attrs={"td": {"class": "text-end font-monospace"}},
    )
    actions = tables.TemplateColumn(
        template_name="editors/includes/assignment_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = EditorAssignment
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "editor",
            "creator",
            "role",
            "status",
            "is_primary",
            "agreed_video_rate",
            "agreed_short_rate",
            "start_date",
            "end_date",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class EditingTaskTable(tables.Table):
    title = tables.Column(linkify=True)
    editor = tables.Column(linkify=True)
    creator = tables.Column(linkify=True)
    agreed_cost = tables.Column(attrs={"td": {"class": "text-end font-monospace"}})
    actions = tables.TemplateColumn(
        template_name="editors/includes/task_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = EditingTask
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "title",
            "editor",
            "creator",
            "task_type",
            "priority",
            "status",
            "deadline",
            "revision_count",
            "agreed_cost",
            "is_paid",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class TaskRevisionTable(tables.Table):
    task = tables.Column(linkify=True)
    render_url = tables.TemplateColumn(
        '<a href="{{ record.render_url }}" target="_blank" '
        'rel="noopener noreferrer">Ver Render</a>',
        verbose_name="Corte",
    )

    class Meta:
        model = TaskRevision
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "task",
            "revision_number",
            "status",
            "submitted_at",
            "reviewed_at",
            "render_url",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
