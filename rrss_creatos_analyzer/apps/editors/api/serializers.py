from rest_framework import serializers

from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.models import TaskRevision


class EditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editor
        fields = "__all__"


class EditorAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorAssignment
        fields = "__all__"


class EditingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditingTask
        fields = "__all__"


class TaskRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskRevision
        fields = "__all__"
