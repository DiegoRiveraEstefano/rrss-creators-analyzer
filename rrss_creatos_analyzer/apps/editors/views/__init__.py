from .assignments import EditorAssignmentCreateView
from .assignments import EditorAssignmentDeleteView
from .assignments import EditorAssignmentDetailView
from .assignments import EditorAssignmentListView
from .assignments import EditorAssignmentUpdateView
from .editors import EditorCreateView
from .editors import EditorDeleteView
from .editors import EditorDetailView
from .editors import EditorListView
from .editors import EditorUpdateView
from .revisions import TaskRevisionCreateView
from .revisions import TaskRevisionDetailView
from .tasks import EditingTaskCreateView
from .tasks import EditingTaskDeleteView
from .tasks import EditingTaskDetailView
from .tasks import EditingTaskListView
from .tasks import EditingTaskUpdateView

__all__ = [
    "EditingTaskCreateView",
    "EditingTaskDeleteView",
    "EditingTaskDetailView",
    "EditingTaskListView",
    "EditingTaskUpdateView",
    "EditorAssignmentCreateView",
    "EditorAssignmentDeleteView",
    "EditorAssignmentDetailView",
    "EditorAssignmentListView",
    "EditorAssignmentUpdateView",
    "EditorCreateView",
    "EditorDeleteView",
    "EditorDetailView",
    "EditorListView",
    "EditorUpdateView",
    "TaskRevisionCreateView",
    "TaskRevisionDetailView",
]
