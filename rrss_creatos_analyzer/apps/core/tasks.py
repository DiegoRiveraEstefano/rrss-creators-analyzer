from __future__ import annotations

from celery import shared_task
from django.conf import settings

from .demo_cleanup import DemoCleanupService


@shared_task(
    name="rrss_creatos_analyzer.apps.core.tasks.cleanup_expired_demo_data_task",
)
def cleanup_expired_demo_data_task() -> dict[str, int]:
    """Celery task that purges expired demo data when DEMO_MODE is active."""
    if not getattr(settings, "DEMO_MODE", False):
        return {}
    retention_days = int(getattr(settings, "DEMO_DATA_RETENTION_DAYS", 7))
    return DemoCleanupService.purge_expired_data(retention_days=retention_days)
