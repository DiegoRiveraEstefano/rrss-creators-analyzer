from typing import TYPE_CHECKING

from .models import CreatorPayout

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CreatorPayoutSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[CreatorPayout]:
        qs = CreatorPayout.objects.select_related("creator", "contract", "approved_by")
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(creator__user=user)
