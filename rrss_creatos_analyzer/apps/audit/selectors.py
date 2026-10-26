from typing import TYPE_CHECKING

from .models import AuditEvent

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AuditEventSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[AuditEvent]:
        return AuditEvent.objects.all()
