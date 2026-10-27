from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum
from django.utils import timezone

from .choices import AssignmentStatus
from .choices import EditorStatus
from .choices import TaskStatus
from .models import EditingTask
from .models import Editor
from .models import EditorAssignment
from .models import TaskRevision

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.db.models import QuerySet


class EditorSelector:
    @classmethod
    def get_visible_queryset(cls, *, user: AbstractUser) -> QuerySet[Editor]:
        qs = Editor.objects.select_related("user").prefetch_related(
            "tags",
            "assignments",
        )
        if user.is_superuser or user.has_perm("editors.view_editor"):
            return qs

        if getattr(user, "creator_profile", None):
            return qs.filter(assignments__creator=user.creator_profile).distinct()

        if getattr(user, "editor_profile", None):
            return qs.filter(pk=user.editor_profile.pk)

        return qs

    @classmethod
    def get_available_editors(cls) -> QuerySet[Editor]:
        return Editor.objects.filter(status=EditorStatus.ACTIVE)

    @classmethod
    def get_editor_metrics(cls, *, editor_id: int) -> dict[str, Any]:
        tasks = EditingTask.objects.filter(editor_id=editor_id)
        aggregated = tasks.aggregate(
            total_tasks=Count("id"),
            completed_tasks=Count(
                "id",
                filter=Q(status=TaskStatus.COMPLETED),
            ),
            active_tasks=Count(
                "id",
                filter=Q(
                    status__in=[
                        TaskStatus.ASSIGNED,
                        TaskStatus.IN_PROGRESS,
                        TaskStatus.IN_REVIEW,
                        TaskStatus.REVISION_REQUESTED,
                    ],
                ),
            ),
            total_earnings=Sum(
                "agreed_cost",
                filter=Q(status=TaskStatus.COMPLETED),
            ),
            avg_revisions=Avg(
                "revision_count",
                filter=Q(status=TaskStatus.COMPLETED),
            ),
        )
        return {
            "total_tasks": aggregated["total_tasks"] or 0,
            "completed_tasks": aggregated["completed_tasks"] or 0,
            "active_tasks": aggregated["active_tasks"] or 0,
            "total_earnings": aggregated["total_earnings"] or 0,
            "avg_revisions": round(aggregated["avg_revisions"] or 0, 1),
        }


class EditorAssignmentSelector:
    @classmethod
    def get_visible_queryset(
        cls,
        *,
        user: AbstractUser,
    ) -> QuerySet[EditorAssignment]:
        qs = EditorAssignment.objects.select_related("editor", "creator")
        if user.is_superuser or user.has_perm("editors.view_editorassignment"):
            return qs

        if getattr(user, "creator_profile", None):
            return qs.filter(creator=user.creator_profile)

        if getattr(user, "editor_profile", None):
            return qs.filter(editor=user.editor_profile)

        return qs

    @classmethod
    def get_active_assignments_for_creator(
        cls,
        *,
        creator_id: int,
    ) -> QuerySet[EditorAssignment]:
        return EditorAssignment.objects.filter(
            creator_id=creator_id,
            status=AssignmentStatus.ACTIVE,
        ).select_related("editor")


class EditingTaskSelector:
    @classmethod
    def get_visible_queryset(
        cls,
        *,
        user: AbstractUser,
    ) -> QuerySet[EditingTask]:
        qs = EditingTask.objects.select_related(
            "editor",
            "creator",
            "video",
        ).prefetch_related("tags", "revisions")

        if user.is_superuser or user.has_perm("editors.view_editingtask"):
            return qs

        if getattr(user, "creator_profile", None):
            return qs.filter(creator=user.creator_profile)

        if getattr(user, "editor_profile", None):
            return qs.filter(editor=user.editor_profile)

        return qs

    @classmethod
    def get_pending_reviews(
        cls,
        *,
        user: AbstractUser,
    ) -> QuerySet[EditingTask]:
        qs = cls.get_visible_queryset(user=user)
        return qs.filter(
            status__in=[TaskStatus.IN_REVIEW, TaskStatus.REVISION_REQUESTED],
        )

    @classmethod
    def get_overdue_tasks(cls, *, user: AbstractUser) -> QuerySet[EditingTask]:
        qs = cls.get_visible_queryset(user=user)
        today = timezone.localdate()
        return qs.filter(
            deadline__lt=today,
            status__in=[
                TaskStatus.ASSIGNED,
                TaskStatus.IN_PROGRESS,
                TaskStatus.REVISION_REQUESTED,
            ],
        )


class TaskRevisionSelector:
    @classmethod
    def get_visible_queryset(
        cls,
        *,
        user: AbstractUser,
    ) -> QuerySet[TaskRevision]:
        qs = TaskRevision.objects.select_related(
            "task",
            "task__editor",
            "task__creator",
        )
        if user.is_superuser or user.has_perm("editors.view_taskrevision"):
            return qs

        if getattr(user, "creator_profile", None):
            return qs.filter(task__creator=user.creator_profile)

        if getattr(user, "editor_profile", None):
            return qs.filter(task__editor=user.editor_profile)

        return qs
