import logging

from django.db import transaction

from .models import AnalyticsSnapshot

logger = logging.getLogger(__name__)


class AnalyticsSnapshotService:
    @classmethod
    @transaction.atomic
    def save_record(
        cls,
        *,
        instance: AnalyticsSnapshot | None = None,
        **data,
    ) -> AnalyticsSnapshot:
        obj = instance or AnalyticsSnapshot()
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        logger.info("analytics_snapshot_saved", extra={"record_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_record(cls, *, instance: AnalyticsSnapshot) -> None:
        rid = instance.id
        instance.delete()
        logger.info("analytics_snapshot_deleted", extra={"record_id": rid})
