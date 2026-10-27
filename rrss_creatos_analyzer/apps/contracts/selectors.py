from typing import TYPE_CHECKING

from .models import Contract

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ContractSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Contract]:
        qs = Contract.objects.select_related("creator")
        if (
            user.is_superuser
            or user.has_perm("contracts.manage_contracts")
            or user.has_perm("creators.view_all_creators")
        ):
            return qs
        return qs.filter(creator__user=user)
