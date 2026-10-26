from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import EditingTask
from .models import Editor
from .models import EditorAssignment
from .models import TaskRevision


class EditorAssignmentInline(admin.TabularInline):
    model = EditorAssignment
    extra = 0


class EditingTaskInline(admin.TabularInline):
    model = EditingTask
    extra = 0
    fields = ("title", "creator", "status", "deadline", "agreed_cost", "is_paid")


class TaskRevisionInline(admin.TabularInline):
    model = TaskRevision
    extra = 0


@admin.register(Editor)
class EditorAdmin(SimpleHistoryAdmin):
    list_display = (
        "name",
        "handle",
        "status",
        "editor_type",
        "primary_specialty",
        "rate_model",
        "base_video_rate",
        "base_short_rate",
        "max_active_tasks",
    )
    list_filter = ("status", "editor_type", "primary_specialty", "rate_model")
    search_fields = ("name", "handle", "email", "discord_handle")
    prepopulated_fields = {"slug": ("handle",)}
    inlines = [EditorAssignmentInline, EditingTaskInline]


@admin.register(EditorAssignment)
class EditorAssignmentAdmin(SimpleHistoryAdmin):
    list_display = (
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
    list_filter = ("status", "role", "is_primary")
    search_fields = ("editor__name", "creator__display_name")


@admin.register(EditingTask)
class EditingTaskAdmin(SimpleHistoryAdmin):
    list_display = (
        "title",
        "editor",
        "creator",
        "video",
        "task_type",
        "status",
        "priority",
        "deadline",
        "revision_count",
        "agreed_cost",
        "is_paid",
    )
    list_filter = ("status", "priority", "task_type", "is_paid")
    search_fields = (
        "title",
        "editor__name",
        "creator__display_name",
        "video__title",
    )
    inlines = [TaskRevisionInline]


@admin.register(TaskRevision)
class TaskRevisionAdmin(SimpleHistoryAdmin):
    list_display = (
        "task",
        "revision_number",
        "status",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = ("status",)
    search_fields = ("task__title", "change_summary", "feedback_notes")
