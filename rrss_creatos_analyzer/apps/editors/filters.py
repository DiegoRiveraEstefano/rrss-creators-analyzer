import django_filters

from .models import EditingTask
from .models import Editor
from .models import EditorAssignment
from .models import TaskRevision


class EditorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Nombre / Estudio")
    handle = django_filters.CharFilter(lookup_expr="icontains", label="Handle (@)")

    class Meta:
        model = Editor
        fields = [
            "name",
            "handle",
            "status",
            "editor_type",
            "primary_specialty",
            "rate_model",
        ]


class EditorAssignmentFilter(django_filters.FilterSet):
    class Meta:
        model = EditorAssignment
        fields = ["editor", "creator", "role", "status", "is_primary"]


class EditingTaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", label="Título de Tarea")

    class Meta:
        model = EditingTask
        fields = [
            "title",
            "editor",
            "creator",
            "video",
            "status",
            "priority",
            "task_type",
            "is_paid",
        ]


class TaskRevisionFilter(django_filters.FilterSet):
    class Meta:
        model = TaskRevision
        fields = ["task", "status"]
