from django.urls import path

from .views import EditingTaskCreateView
from .views import EditingTaskDeleteView
from .views import EditingTaskDetailView
from .views import EditingTaskListView
from .views import EditingTaskUpdateView
from .views import EditorAssignmentCreateView
from .views import EditorAssignmentDeleteView
from .views import EditorAssignmentDetailView
from .views import EditorAssignmentListView
from .views import EditorAssignmentUpdateView
from .views import EditorCreateView
from .views import EditorDeleteView
from .views import EditorDetailView
from .views import EditorListView
from .views import EditorUpdateView
from .views import TaskRevisionCreateView
from .views import TaskRevisionDetailView

app_name = "editors"

urlpatterns = [
    # List and Create Editor
    path("", EditorListView.as_view(), name="editor_list"),
    path("create/", EditorCreateView.as_view(), name="editor_create"),
    # Assignments (Fixed prefixes before slug patterns)
    path(
        "assignments/",
        EditorAssignmentListView.as_view(),
        name="assignment_list",
    ),
    path(
        "assignments/create/",
        EditorAssignmentCreateView.as_view(),
        name="assignment_create",
    ),
    path(
        "assignments/<int:pk>/",
        EditorAssignmentDetailView.as_view(),
        name="assignment_detail",
    ),
    path(
        "assignments/<int:pk>/edit/",
        EditorAssignmentUpdateView.as_view(),
        name="assignment_update",
    ),
    path(
        "assignments/<int:pk>/delete/",
        EditorAssignmentDeleteView.as_view(),
        name="assignment_delete",
    ),
    # Editing Tasks (Fixed prefixes before slug patterns)
    path("tasks/", EditingTaskListView.as_view(), name="task_list"),
    path("tasks/create/", EditingTaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", EditingTaskDetailView.as_view(), name="task_detail"),
    path(
        "tasks/<int:pk>/edit/",
        EditingTaskUpdateView.as_view(),
        name="task_update",
    ),
    path(
        "tasks/<int:pk>/delete/",
        EditingTaskDeleteView.as_view(),
        name="task_delete",
    ),
    # Revisions
    path(
        "tasks/<int:task_id>/revisions/create/",
        TaskRevisionCreateView.as_view(),
        name="revision_create",
    ),
    path(
        "revisions/<int:pk>/",
        TaskRevisionDetailView.as_view(),
        name="revision_detail",
    ),
    # Editor detail/edit/delete by slug (After fixed paths)
    path("<slug:slug>/", EditorDetailView.as_view(), name="editor_detail"),
    path("<slug:slug>/edit/", EditorUpdateView.as_view(), name="editor_update"),
    path("<slug:slug>/delete/", EditorDeleteView.as_view(), name="editor_delete"),
]
