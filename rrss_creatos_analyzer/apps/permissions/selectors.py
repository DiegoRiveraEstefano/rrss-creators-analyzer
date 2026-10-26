from typing import TYPE_CHECKING

from .models import RoleGroupProfile

if TYPE_CHECKING:
    from django.db.models import QuerySet


class RoleGroupProfileSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[RoleGroupProfile]:
        return RoleGroupProfile.objects.select_related("group").prefetch_related(
            "group__permissions",
        )
