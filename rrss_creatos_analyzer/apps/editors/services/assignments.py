import logging

from django.db import transaction
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.editors.choices import AssignmentStatus
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment

logger = logging.getLogger(__name__)


class EditorAssignmentService:
    @classmethod
    @transaction.atomic
    def save_assignment(
        cls,
        *,
        instance: EditorAssignment | None = None,
        **data,
    ) -> EditorAssignment:
        assignment = instance or EditorAssignment()

        start_date = data.get("start_date", getattr(assignment, "start_date", None))
        end_date = data.get("end_date", getattr(assignment, "end_date", None))
        if start_date and end_date and start_date > end_date:
            msg = (
                "La fecha de inicio de la asignación no puede ser "
                "posterior a la fecha de fin."
            )
            raise BusinessLogicError(msg)

        is_primary = data.get("is_primary", getattr(assignment, "is_primary", False))
        creator = data.get("creator", getattr(assignment, "creator", None))
        role = data.get("role", getattr(assignment, "role", None))

        if is_primary and creator and role:
            qs = EditorAssignment.objects.filter(
                creator=creator,
                role=role,
                is_primary=True,
            )
            if assignment.pk:
                qs = qs.exclude(pk=assignment.pk)
            qs.update(is_primary=False)

        for field, value in data.items():
            setattr(assignment, field, value)
        assignment.save()

        logger.info(
            "editor_assignment_saved",
            extra={
                "assignment_id": assignment.id,
                "editor_id": assignment.editor_id,
                "creator_id": assignment.creator_id,
            },
        )
        return assignment

    @classmethod
    @transaction.atomic
    def end_assignment(
        cls,
        *,
        instance: EditorAssignment,
        end_date=None,
    ) -> EditorAssignment:
        instance.status = AssignmentStatus.ENDED
        instance.end_date = end_date or timezone.localdate()
        instance.save()
        logger.info(
            "editor_assignment_ended",
            extra={"assignment_id": instance.id},
        )
        return instance

    @classmethod
    @transaction.atomic
    def delete_assignment(cls, *, instance: EditorAssignment) -> None:
        assignment_id = instance.id
        instance.delete()
        logger.info("editor_assignment_deleted", extra={"assignment_id": assignment_id})
