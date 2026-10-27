import logging

from django.utils import timezone

from config import celery_app
from rrss_creatos_analyzer.apps.editors.choices import TaskStatus
from rrss_creatos_analyzer.apps.editors.models import EditingTask

logger = logging.getLogger(__name__)


@celery_app.task(name="editors.check_overdue_tasks")
def check_overdue_tasks() -> int:
    """Celery task to flag or alert on overdue editing tasks."""
    today = timezone.localdate()
    overdue_qs = EditingTask.objects.filter(
        deadline__lt=today,
        status__in=[
            TaskStatus.ASSIGNED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.REVISION_REQUESTED,
        ],
    )
    count = overdue_qs.count()
    logger.info("overdue_editing_tasks_checked", extra={"overdue_count": count})
    return count
