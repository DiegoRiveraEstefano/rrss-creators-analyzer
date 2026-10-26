import logging

from django.db import transaction

from .models import ExportJob

logger = logging.getLogger(__name__)


class ExportJobService:
    @classmethod
    @transaction.atomic
    def save_record(cls, *, instance: ExportJob | None = None, **data) -> ExportJob:
        obj = instance or ExportJob()
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        logger.info("exports_export_saved", extra={"record_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_record(cls, *, instance: ExportJob) -> None:
        rid = instance.id
        instance.delete()
        logger.info("exports_export_deleted", extra={"record_id": rid})
