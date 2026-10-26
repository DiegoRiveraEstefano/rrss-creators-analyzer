from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.editors.choices import EditorAssignmentRole
from rrss_creatos_analyzer.apps.editors.choices import EditorStatus
from rrss_creatos_analyzer.apps.editors.choices import RevisionStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskType
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.services import EditingTaskService
from rrss_creatos_analyzer.apps.editors.services import EditorAssignmentService
from rrss_creatos_analyzer.apps.editors.services import EditorService

from .factories import EditingTaskFactory
from .factories import EditorFactory

pytestmark = pytest.mark.django_db


class TestEditorService:
    def test_save_editor_happy_path(self):
        editor = EditorService.save_editor(
            name="John Doe",
            handle="johndoe",
            slug="johndoe",
            base_video_rate=Decimal("200.00"),
            max_active_tasks=3,
        )
        assert editor.pk is not None
        assert editor.name == "John Doe"
        assert editor.base_video_rate == Decimal("200.00")

    def test_save_editor_invalid_capacity_raises_error(self):
        with pytest.raises(BusinessLogicError, match="capacidad máxima"):
            EditorService.save_editor(
                name="John Doe",
                handle="johndoe2",
                slug="johndoe2",
                max_active_tasks=0,
            )

    def test_save_editor_negative_rate_raises_error(self):
        with pytest.raises(BusinessLogicError, match="no puede ser negativo"):
            EditorService.save_editor(
                name="John Doe",
                handle="johndoe3",
                slug="johndoe3",
                base_video_rate=Decimal("-50.00"),
            )

    def test_delete_editor_with_active_tasks_raises_error(self):
        editor = EditorFactory()
        EditingTaskFactory(editor=editor, status=TaskStatus.IN_PROGRESS)

        with pytest.raises(BusinessLogicError, match="tareas de edición en curso"):
            EditorService.delete_editor(instance=editor)

    def test_delete_editor_without_active_tasks(self):
        editor = EditorFactory()
        EditorService.delete_editor(instance=editor)
        assert not Editor.objects.filter(pk=editor.pk).exists()


class TestEditorAssignmentService:
    def test_save_assignment_happy_path(self):
        creator = CreatorFactory()
        editor = EditorFactory()
        assignment = EditorAssignmentService.save_assignment(
            creator=creator,
            editor=editor,
            role=EditorAssignmentRole.LEAD_EDITOR,
            start_date=timezone.localdate(),
            is_primary=True,
        )
        assert assignment.pk is not None
        assert assignment.is_primary is True

    def test_save_assignment_exclusive_primary(self):
        creator = CreatorFactory()
        ed1 = EditorFactory()
        ed2 = EditorFactory()

        asg1 = EditorAssignmentService.save_assignment(
            creator=creator,
            editor=ed1,
            role=EditorAssignmentRole.LEAD_EDITOR,
            start_date=timezone.localdate(),
            is_primary=True,
        )
        asg2 = EditorAssignmentService.save_assignment(
            creator=creator,
            editor=ed2,
            role=EditorAssignmentRole.LEAD_EDITOR,
            start_date=timezone.localdate(),
            is_primary=True,
        )

        asg1.refresh_from_db()
        assert asg1.is_primary is False
        assert asg2.is_primary is True

    def test_save_assignment_invalid_dates(self):
        today = timezone.localdate()
        with pytest.raises(BusinessLogicError, match="no puede ser posterior"):
            EditorAssignmentService.save_assignment(
                creator=CreatorFactory(),
                editor=EditorFactory(),
                role=EditorAssignmentRole.LEAD_EDITOR,
                start_date=today,
                end_date=today - timedelta(days=5),
            )


class TestEditingTaskService:
    def test_create_task_happy_path(self):
        creator = CreatorFactory()
        editor = EditorFactory(base_video_rate=Decimal("180.00"), max_active_tasks=5)
        today = timezone.localdate()

        task = EditingTaskService.create_task(
            creator=creator,
            editor=editor,
            title="Video Gameplay 1",
            assigned_date=today,
            deadline=today + timedelta(days=3),
            task_type=TaskType.LONG_FORM_EDIT,
        )
        assert task.pk is not None
        assert task.status == TaskStatus.ASSIGNED
        assert task.agreed_cost == Decimal("180.00")

    def test_create_task_inactive_editor_raises_error(self):
        editor = EditorFactory(status=EditorStatus.INACTIVE)
        today = timezone.localdate()
        with pytest.raises(BusinessLogicError, match="se encuentra inactivo"):
            EditingTaskService.create_task(
                creator=CreatorFactory(),
                editor=editor,
                title="Test Video",
                assigned_date=today,
                deadline=today + timedelta(days=2),
            )

    def test_create_task_capacity_reached_raises_error(self):
        editor = EditorFactory(max_active_tasks=1)
        EditingTaskFactory(editor=editor, status=TaskStatus.IN_PROGRESS)
        today = timezone.localdate()

        with pytest.raises(BusinessLogicError, match="capacidad máxima"):
            EditingTaskService.create_task(
                creator=CreatorFactory(),
                editor=editor,
                title="Another task",
                assigned_date=today,
                deadline=today + timedelta(days=2),
            )

    def test_submit_revision_and_review(self):
        task = EditingTaskFactory(revision_count=0, status=TaskStatus.IN_PROGRESS)

        # Submit revision
        rev = EditingTaskService.submit_revision(
            task=task,
            render_url="https://vimeo.com/test1",
            change_summary="Primer corte terminado",
        )
        task.refresh_from_db()
        assert task.revision_count == 1
        assert task.status == TaskStatus.IN_REVIEW
        assert rev.status == RevisionStatus.PENDING_REVIEW

        # Review with changes requested
        EditingTaskService.review_revision(
            revision=rev,
            approved=False,
            feedback="Por favor corregir el audio en el minuto 2",
        )
        task.refresh_from_db()
        rev.refresh_from_db()
        assert rev.status == RevisionStatus.CHANGES_REQUESTED
        assert task.status == TaskStatus.REVISION_REQUESTED

        # Submit revision 2
        rev2 = EditingTaskService.submit_revision(
            task=task,
            render_url="https://vimeo.com/test2",
            change_summary="Audio corregido",
        )
        assert task.revision_count == 2  # noqa: PLR2004

        # Approve revision 2
        EditingTaskService.review_revision(
            revision=rev2,
            approved=True,
            feedback="Excelente trabajo, aprobado",
        )
        task.refresh_from_db()
        rev2.refresh_from_db()
        assert rev2.status == RevisionStatus.APPROVED
        assert task.status == TaskStatus.APPROVED
        assert task.final_render_url == "https://vimeo.com/test2"

    def test_complete_and_pay_task(self):
        task = EditingTaskFactory(status=TaskStatus.APPROVED)
        EditingTaskService.complete_task(task=task)
        assert task.status == TaskStatus.COMPLETED
        assert task.delivered_at is not None

        EditingTaskService.mark_as_paid(task=task)
        assert task.is_paid is True
        assert task.paid_at is not None
