from typing import TYPE_CHECKING

from .models import ImportBatch

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ImportBatchSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[ImportBatch]:
        return ImportBatch.objects.select_related("uploaded_by")
