from typing import TYPE_CHECKING

from .models import ExportJob

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ExportJobSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[ExportJob]:
        return ExportJob.objects.all()
