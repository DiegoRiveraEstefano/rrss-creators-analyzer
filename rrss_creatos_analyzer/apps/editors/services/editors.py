import logging
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.models import Editor

logger = logging.getLogger(__name__)


class EditorService:
    @classmethod
    @transaction.atomic
    def save_editor(
        cls,
        *,
        instance: Editor | None = None,
        tags=None,
        **data,
    ) -> Editor:
        editor = instance or Editor()

        max_tasks = data.get("max_active_tasks", getattr(editor, "max_active_tasks", 3))
        if max_tasks is not None and max_tasks < 1:
            msg = "La capacidad máxima de tareas simultáneas debe ser al menos 1."
            raise BusinessLogicError(msg)

        rate_fields = [
            "base_video_rate",
            "base_short_rate",
            "hourly_rate",
            "monthly_retainer",
        ]
        for field in rate_fields:
            if (
                field in data
                and data[field] is not None
                and data[field] < Decimal("0.00")
            ):
                msg = f"El valor de {field} no puede ser negativo."
                raise BusinessLogicError(msg)

        for field, value in data.items():
            setattr(editor, field, value)
        editor.save()

        if tags is not None:
            editor.tags.set(tags)

        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "editor_saved",
            extra={"editor_id": editor.id, "handle": editor.handle},
        )
        return editor

    @classmethod
    @transaction.atomic
    def delete_editor(cls, *, instance: Editor) -> None:
        has_active_tasks = instance.editing_tasks.filter(
            status__in=[
                TaskStatus.ASSIGNED,
                TaskStatus.IN_PROGRESS,
                TaskStatus.IN_REVIEW,
                TaskStatus.REVISION_REQUESTED,
            ],
        ).exists()
        if has_active_tasks:
            msg = (
                "No se puede eliminar un editor que tiene tareas de edición en curso. "
                "Finalice o reasigne sus tareas antes de continuar."
            )
            raise BusinessLogicError(msg)

        editor_id = instance.id
        instance.delete()
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info("editor_deleted", extra={"editor_id": editor_id})
