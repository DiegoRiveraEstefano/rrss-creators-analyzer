from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.editors.choices import AssignmentStatus
from rrss_creatos_analyzer.apps.editors.choices import EditorStatus
from rrss_creatos_analyzer.apps.editors.choices import RevisionStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.choices import TaskType
from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.models import TaskRevision

if TYPE_CHECKING:
    from rrss_creatos_analyzer.apps.creators.models import Creator
    from rrss_creatos_analyzer.apps.videos.models import Video

logger = logging.getLogger(__name__)


class EditingTaskService:
    @classmethod
    @transaction.atomic
    def create_task(  # noqa: C901, PLR0913
        cls,
        *,
        creator: Creator,
        editor: Editor,
        title: str,
        deadline,
        assigned_date=None,
        video: Video | None = None,
        task_type: str = TaskType.LONG_FORM_EDIT,
        priority: str = "medium",
        agreed_cost: Decimal | None = None,
        brief: str = "",
        raw_footage_url: str = "",
        tags=None,
        **extra_data,
    ) -> EditingTask:
        if editor.status == EditorStatus.INACTIVE:
            msg = (
                f"El editor {editor.name} se encuentra inactivo "
                "y no puede recibir nuevas tareas."
            )
            raise BusinessLogicError(msg)

        if not assigned_date:
            assigned_date = timezone.localdate()

        if deadline < assigned_date:
            msg = (
                "La fecha límite (deadline) no puede ser "
                "anterior a la fecha de asignación."
            )
            raise BusinessLogicError(msg)

        active_tasks_count = editor.editing_tasks.filter(
            status__in=[
                TaskStatus.ASSIGNED,
                TaskStatus.IN_PROGRESS,
                TaskStatus.IN_REVIEW,
                TaskStatus.REVISION_REQUESTED,
            ],
        ).count()
        if active_tasks_count >= editor.max_active_tasks:
            msg = (
                f"El editor {editor.name} ha alcanzado su capacidad máxima "
                f"de {editor.max_active_tasks} tareas simultáneas activas."
            )
            raise BusinessLogicError(msg)

        if agreed_cost is None:
            assignment = EditorAssignment.objects.filter(
                editor=editor,
                creator=creator,
                status=AssignmentStatus.ACTIVE,
            ).first()

            if task_type in [TaskType.SHORT_VERTICAL, TaskType.THUMBNAIL]:
                agreed_cost = (
                    assignment.agreed_short_rate
                    if assignment and assignment.agreed_short_rate is not None
                    else editor.base_short_rate
                )
            else:
                agreed_cost = (
                    assignment.agreed_video_rate
                    if assignment and assignment.agreed_video_rate is not None
                    else editor.base_video_rate
                )

        cost = agreed_cost or Decimal("0.00")
        task = EditingTask.objects.create(
            title=title,
            creator=creator,
            editor=editor,
            video=video,
            task_type=task_type,
            priority=priority,
            assigned_date=assigned_date,
            deadline=deadline,
            agreed_cost=cost,
            brief=brief,
            raw_footage_url=raw_footage_url,
            status=TaskStatus.ASSIGNED,
            **extra_data,
        )

        if tags is not None:
            task.tags.set(tags)

        if video:
            if task_type == TaskType.THUMBNAIL:
                video.thumbnail_cost = cost
            else:
                video.editing_cost = cost
            video.total_production_cost = (
                video.production_cost + video.editing_cost + video.thumbnail_cost
            )
            if editor.user and not video.assigned_editor:
                video.assigned_editor = editor.user
            video.save()

        logger.info(
            "editing_task_created",
            extra={
                "task_id": task.id,
                "editor_id": editor.id,
                "creator_id": creator.id,
                "video_id": video.id if video else None,
            },
        )
        return task

    @classmethod
    @transaction.atomic
    def start_task(cls, *, task: EditingTask) -> EditingTask:
        if task.status != TaskStatus.ASSIGNED:
            msg = "Solo se pueden iniciar tareas en estado asignado."
            raise BusinessLogicError(msg)
        task.status = TaskStatus.IN_PROGRESS
        task.save()
        logger.info("editing_task_started", extra={"task_id": task.id})
        return task

    @classmethod
    @transaction.atomic
    def update_task(
        cls,
        *,
        instance: EditingTask,
        tags=None,
        **data,
    ) -> EditingTask:
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if instance.video and "agreed_cost" in data:
            v = instance.video
            if instance.task_type == TaskType.THUMBNAIL:
                v.thumbnail_cost = instance.agreed_cost
            else:
                v.editing_cost = instance.agreed_cost
            v.total_production_cost = (
                v.production_cost + v.editing_cost + v.thumbnail_cost
            )
            v.save()

        logger.info("editing_task_updated", extra={"task_id": instance.id})
        return instance

    @classmethod
    @transaction.atomic
    def submit_revision(
        cls,
        *,
        task: EditingTask,
        render_url: str,
        change_summary: str = "",
    ) -> TaskRevision:
        if not render_url:
            msg = (
                "Debe proporcionar una URL válida para el corte / render de la versión."
            )
            raise BusinessLogicError(msg)

        if task.status in [
            TaskStatus.APPROVED,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ]:
            msg = (
                "No se pueden enviar revisiones para una tarea que ya está aprobada, "
                "completada o cancelada."
            )
            raise BusinessLogicError(msg)

        if task.revisions.filter(status=RevisionStatus.PENDING_REVIEW).exists():
            msg = (
                "No se puede enviar una nueva versión mientras exista una entrega "
                "pendiente de revisión."
            )
            raise BusinessLogicError(msg)

        task.revision_count += 1
        task.preview_render_url = render_url
        task.status = TaskStatus.IN_REVIEW
        task.save()

        revision = TaskRevision.objects.create(
            task=task,
            revision_number=task.revision_count,
            render_url=render_url,
            change_summary=change_summary,
            status=RevisionStatus.PENDING_REVIEW,
            submitted_at=timezone.now(),
        )

        logger.info(
            "task_revision_submitted",
            extra={
                "task_id": task.id,
                "revision_id": revision.id,
                "revision_number": task.revision_count,
            },
        )
        return revision

    @classmethod
    @transaction.atomic
    def review_revision(
        cls,
        *,
        revision: TaskRevision,
        approved: bool,
        feedback: str = "",
    ) -> EditingTask:
        task = revision.task
        now = timezone.now()

        revision.reviewed_at = now
        revision.feedback_notes = feedback

        if approved:
            revision.status = RevisionStatus.APPROVED
            revision.save()

            task.status = TaskStatus.APPROVED
            task.approved_at = now
            task.final_render_url = revision.render_url
            task.save()

            if task.video:
                task.video.master_asset_url = revision.render_url
                if task.task_type == TaskType.THUMBNAIL:
                    task.video.thumbnail_cost = task.agreed_cost
                else:
                    task.video.editing_cost = task.agreed_cost
                task.video.total_production_cost = (
                    task.video.production_cost
                    + task.video.editing_cost
                    + task.video.thumbnail_cost
                )
                if task.video.status in [
                    VideoStatus.RECORDING,
                    VideoStatus.EDITING,
                    VideoStatus.REVIEW,
                ]:
                    task.video.status = VideoStatus.READY
                task.video.save()
        else:
            revision.status = RevisionStatus.CHANGES_REQUESTED
            revision.save()

            task.status = TaskStatus.REVISION_REQUESTED
            task.save()

        logger.info(
            "task_revision_reviewed",
            extra={
                "task_id": task.id,
                "revision_id": revision.id,
                "approved": approved,
            },
        )
        return task

    @classmethod
    @transaction.atomic
    def complete_task(
        cls,
        *,
        task: EditingTask,
        final_render_url: str = "",
    ) -> EditingTask:
        if final_render_url:
            task.final_render_url = final_render_url

        task.status = TaskStatus.COMPLETED
        task.delivered_at = task.delivered_at or timezone.now()
        task.save()

        if task.video and task.final_render_url:
            task.video.master_asset_url = task.final_render_url
            task.video.save()

        logger.info("editing_task_completed", extra={"task_id": task.id})
        return task

    @classmethod
    @transaction.atomic
    def mark_as_paid(cls, *, task: EditingTask) -> EditingTask:
        if task.status not in [TaskStatus.APPROVED, TaskStatus.COMPLETED]:
            msg = (
                "Solo se pueden liquidar tareas que hayan sido previamente "
                "aprobadas o completadas."
            )
            raise BusinessLogicError(msg)

        task.is_paid = True
        task.paid_at = timezone.now()
        if task.status == TaskStatus.APPROVED:
            task.status = TaskStatus.COMPLETED
        task.save()
        logger.info("editing_task_paid", extra={"task_id": task.id})
        return task

    @classmethod
    @transaction.atomic
    def delete_task(cls, *, instance: EditingTask) -> None:
        task_id = instance.id
        instance.delete()
        logger.info("editing_task_deleted", extra={"task_id": task_id})


class TaskRevisionService:
    @classmethod
    @transaction.atomic
    def save_revision(
        cls,
        *,
        instance: TaskRevision | None = None,
        **data,
    ) -> TaskRevision:
        rev = instance or TaskRevision()
        for field, value in data.items():
            setattr(rev, field, value)
        rev.save()
        logger.info("task_revision_saved", extra={"revision_id": rev.id})
        return rev

    @classmethod
    @transaction.atomic
    def delete_revision(cls, *, instance: TaskRevision) -> None:
        rid = instance.id
        instance.delete()
        logger.info("task_revision_deleted", extra={"revision_id": rid})
