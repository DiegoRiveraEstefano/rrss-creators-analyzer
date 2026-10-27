import pytest
from django.db.utils import IntegrityError

from .factories import EditingTaskFactory
from .factories import EditorAssignmentFactory
from .factories import EditorFactory
from .factories import TaskRevisionFactory

pytestmark = pytest.mark.django_db


class TestEditorModel:
    def test_str_and_get_absolute_url(self):
        editor = EditorFactory(name="Alex Miller", handle="alexedit")
        assert "Alex Miller (@alexedit)" in str(editor)
        assert editor.get_absolute_url() == f"/editors/{editor.slug}/"

    def test_unique_handle_constraint(self):
        EditorFactory(handle="duplicate_tag")
        with pytest.raises(IntegrityError):
            EditorFactory(handle="duplicate_tag")


class TestEditorAssignmentModel:
    def test_str_and_get_absolute_url(self):
        assignment = EditorAssignmentFactory()
        assert assignment.editor.name in str(assignment)
        assert assignment.creator.display_name in str(assignment)
        assert assignment.get_absolute_url() == f"/editors/assignments/{assignment.pk}/"

    def test_unique_editor_creator_role_constraint(self):
        assignment = EditorAssignmentFactory()
        with pytest.raises(IntegrityError):
            EditorAssignmentFactory(
                editor=assignment.editor,
                creator=assignment.creator,
                role=assignment.role,
            )


class TestEditingTaskModel:
    def test_str_and_get_absolute_url(self):
        task = EditingTaskFactory(title="YouTube VOD #45")
        assert "YouTube VOD #45" in str(task)
        assert task.get_absolute_url() == f"/editors/tasks/{task.pk}/"


class TestTaskRevisionModel:
    def test_str_and_get_absolute_url(self):
        rev = TaskRevisionFactory(revision_number=1)
        assert "v1" in str(rev)
        assert rev.get_absolute_url() == f"/editors/revisions/{rev.pk}/"
