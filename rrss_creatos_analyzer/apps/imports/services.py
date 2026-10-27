import logging

from django.db import transaction

from .models import ImportBatch

logger = logging.getLogger(__name__)


class ImportBatchService:
    @classmethod
    @transaction.atomic
    def save_batch(cls, *, instance: ImportBatch | None = None, **data) -> ImportBatch:
        batch = instance or ImportBatch()
        for field, value in data.items():
            setattr(batch, field, value)
        batch.save()
        logger.info(
            "import_batch_saved",
            extra={"batch_id": batch.id, "batch_filename": batch.filename},
        )
        return batch

    @classmethod
    @transaction.atomic
    def delete_batch(cls, *, instance: ImportBatch) -> None:
        batch_id = instance.id
        instance.delete()
        logger.info("import_batch_deleted", extra={"batch_id": batch_id})
