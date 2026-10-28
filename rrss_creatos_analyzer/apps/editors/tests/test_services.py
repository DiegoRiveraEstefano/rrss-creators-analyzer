from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import VideoStatus
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
from rrss_creatos_analyzer.apps.videos.models import Video

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

    def test_delete_editor_without_active_tasks_succeeds(self):
        editor = EditorFactory()
        EditingTaskFactory(editor=editor, status=TaskStatus.COMPLETED)

        EditorService.delete_editor(instance=editor)
        assert not Editor.objects.filter(pk=editor.pk).exists()


class TestEditorAssignmentService:
    def test_save_assignment_happy_path(self):
        editor = EditorFactory()
        creator = CreatorFactory()
        start = timezone.localdate()

        assignment = EditorAssignmentService.save_assignment(
            editor=editor,
            creator=creator,
            role=EditorAssignmentRole.LEAD_EDITOR,
            start_date=start,
            agreed_video_rate=Decimal("180.00"),
        )
        assert assignment.pk is not None
        assert assignment.agreed_video_rate == Decimal("180.00")

    def test_save_assignment_exclusive_primary(self):
        editor1 = EditorFactory()
        editor2 = EditorFactory()
        creator = CreatorFactory()
        start = timezone.localdate()

        a1 = EditorAssignmentService.save_assignment(
            editor=editor1,
            creator=creator,
            role=EditorAssignmentRole.LEAD_EDITOR,
            start_date=start,
            is_primary=True,
        )
        assert a1.is_primary is True

        a2 = EditorAssignmentService.save_assignment(
            editor=editor2,
            creator=creator,
            role=EditorAssignmentRole.LEAD_EDITOR,
            start_date=start,
            is_primary=True,
        )
        a1.refresh_from_db()
        assert a2.is_primary is True
        assert a1.is_primary is False

    def test_save_assignment_invalid_dates_raises_error(self):
        editor = EditorFactory()
        creator = CreatorFactory()
        start = timezone.localdate()

        with pytest.raises(BusinessLogicError, match="no puede ser posterior"):
            EditorAssignmentService.save_assignment(
                editor=editor,
                creator=creator,
                role=EditorAssignmentRole.LEAD_EDITOR,
                start_date=start,
                end_date=start - timedelta(days=1),
            )


class TestEditingTaskService:
    def test_create_task_happy_path(self):
        editor = EditorFactory(base_video_rate=Decimal("150.00"))
        creator = CreatorFactory()
        today = timezone.localdate()

        task = EditingTaskService.create_task(
            creator=creator,
            editor=editor,
            title="Video #1",
            deadline=today + timedelta(days=3),
        )
        assert task.pk is not None
        assert task.agreed_cost == Decimal("150.00")
        assert task.status == TaskStatus.ASSIGNED

    def test_create_task_inactive_editor_raises_error(self):
        editor = EditorFactory(status=EditorStatus.INACTIVE)
        creator = CreatorFactory()
        today = timezone.localdate()

        with pytest.raises(BusinessLogicError, match="se encuentra inactivo"):
            EditingTaskService.create_task(
                creator=creator,
                editor=editor,
                title="Video #1",
                deadline=today + timedelta(days=3),
            )

    def test_create_task_max_capacity_reached_raises_error(self):
        editor = EditorFactory(max_active_tasks=1)
        creator = CreatorFactory()
        today = timezone.localdate()

        EditingTaskFactory(editor=editor, status=TaskStatus.ASSIGNED)

        with pytest.raises(BusinessLogicError, match="capacidad máxima"):
            EditingTaskService.create_task(
                creator=creator,
                editor=editor,
                title="Video #2",
                deadline=today + timedelta(days=3),
            )

    def test_workflow_revision_cycle_and_approval(self):
        task = EditingTaskFactory(status=TaskStatus.ASSIGNED)

        # Submit revision 1
        rev = EditingTaskService.submit_revision(
            task=task,
            render_url="https://vimeo.com/test1",
            change_summary="Primer corte",
        )
        task.refresh_from_db()
        assert task.status == TaskStatus.IN_REVIEW
        assert task.revision_count == 1
        assert rev.status == RevisionStatus.PENDING_REVIEW

        # Request changes on revision 1
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

    def test_start_task(self):
        task = EditingTaskFactory(status=TaskStatus.ASSIGNED)
        started = EditingTaskService.start_task(task=task)
        assert started.status == TaskStatus.IN_PROGRESS

        with pytest.raises(BusinessLogicError, match="estado asignado"):
            EditingTaskService.start_task(task=started)

    def test_submit_revision_when_pending_revision_exists_raises_error(self):
        task = EditingTaskFactory(status=TaskStatus.ASSIGNED)
        EditingTaskService.submit_revision(
            task=task,
            render_url="https://vimeo.com/test1",
        )
        with pytest.raises(BusinessLogicError, match="pendiente de revisión"):
            EditingTaskService.submit_revision(
                task=task,
                render_url="https://vimeo.com/test2",
            )

    def test_submit_revision_on_approved_task_raises_error(self):
        task = EditingTaskFactory(status=TaskStatus.APPROVED)
        with pytest.raises(BusinessLogicError, match="ya está aprobada"):
            EditingTaskService.submit_revision(
                task=task,
                render_url="https://vimeo.com/test3",
            )

    def test_thumbnail_task_imputation_and_status_advance(self):
        creator = CreatorFactory()
        editor = EditorFactory(base_short_rate=Decimal("40.00"))
        video = Video.objects.create(
            creator=creator,
            title="Video Master Test",
            status=VideoStatus.EDITING,
            production_cost=Decimal("100.00"),
        )
        today = timezone.localdate()

        task = EditingTaskService.create_task(
            creator=creator,
            editor=editor,
            video=video,
            title="Diseño de Miniatura",
            task_type=TaskType.THUMBNAIL,
            deadline=today + timedelta(days=2),
        )
        video.refresh_from_db()
        assert video.thumbnail_cost == Decimal("40.00")
        assert video.total_production_cost == Decimal("140.00")

        rev = EditingTaskService.submit_revision(
            task=task,
            render_url="https://drive.google.com/thumb.png",
        )
        EditingTaskService.review_revision(
            revision=rev,
            approved=True,
            feedback="Miniatura aprobada",
        )
        video.refresh_from_db()
        assert video.thumbnail_cost == Decimal("40.00")
        assert video.status == VideoStatus.READY

    def test_complete_and_pay_task(self):
        task = EditingTaskFactory(status=TaskStatus.APPROVED)
        EditingTaskService.complete_task(task=task)
        assert task.status == TaskStatus.COMPLETED
        assert task.delivered_at is not None

        EditingTaskService.mark_as_paid(task=task)
        assert task.is_paid is True
        assert task.paid_at is not None

    def test_mark_as_paid_on_unapproved_task_raises_error(self):
        task = EditingTaskFactory(status=TaskStatus.ASSIGNED)
        with pytest.raises(BusinessLogicError, match="previamente aprobadas"):
            EditingTaskService.mark_as_paid(task=task)

    def test_mark_as_paid_on_approved_transitions_to_completed(self):
        task = EditingTaskFactory(status=TaskStatus.APPROVED)
        EditingTaskService.mark_as_paid(task=task)
        task.refresh_from_db()
        assert task.status == TaskStatus.COMPLETED
        assert task.is_paid is True
