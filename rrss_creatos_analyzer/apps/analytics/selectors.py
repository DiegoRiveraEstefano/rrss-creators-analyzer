from typing import TYPE_CHECKING

from .models import AnalyticsSnapshot

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AnalyticsSnapshotSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[AnalyticsSnapshot]:
        return AnalyticsSnapshot.objects.all()
