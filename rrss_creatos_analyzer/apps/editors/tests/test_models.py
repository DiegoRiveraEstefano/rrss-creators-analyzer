from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone

from rrss_creatos_analyzer.apps.editors.choices import TaskStatus

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

    def test_is_overdue_property(self):
        today = timezone.localdate()
        task_overdue = EditingTaskFactory(
            deadline=today - timedelta(days=2),
            status=TaskStatus.IN_PROGRESS,
        )
        assert task_overdue.is_overdue is True

        task_completed = EditingTaskFactory(
            deadline=today - timedelta(days=2),
            status=TaskStatus.COMPLETED,
        )
        assert task_completed.is_overdue is False

        task_future = EditingTaskFactory(
            deadline=today + timedelta(days=2),
            status=TaskStatus.IN_PROGRESS,
        )
        assert task_future.is_overdue is False

    def test_clean_validation(self):
        today = timezone.localdate()
        task = EditingTaskFactory.build(
            assigned_date=today,
            deadline=today - timedelta(days=1),
        )
        with pytest.raises(ValidationError):
            task.clean()

        task_unpaid = EditingTaskFactory.build(
            status=TaskStatus.ASSIGNED,
            is_paid=True,
        )
        with pytest.raises(ValidationError):
            task_unpaid.clean()


class TestTaskRevisionModel:
    def test_str_and_get_absolute_url(self):
        rev = TaskRevisionFactory(revision_number=1)
        assert "v1" in str(rev)
        assert rev.get_absolute_url() == f"/editors/revisions/{rev.pk}/"
