from rest_framework import viewsets

from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.models import TaskRevision

from .serializers import EditingTaskSerializer
from .serializers import EditorAssignmentSerializer
from .serializers import EditorSerializer
from .serializers import TaskRevisionSerializer


class EditorViewSet(viewsets.ModelViewSet):
    queryset = Editor.objects.all()
    serializer_class = EditorSerializer


class EditorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = EditorAssignment.objects.all()
    serializer_class = EditorAssignmentSerializer


class EditingTaskViewSet(viewsets.ModelViewSet):
    queryset = EditingTask.objects.all()
    serializer_class = EditingTaskSerializer


class TaskRevisionViewSet(viewsets.ModelViewSet):
    queryset = TaskRevision.objects.all()
    serializer_class = TaskRevisionSerializer
