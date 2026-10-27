from typing import TYPE_CHECKING

from .models import CampaignDeliverable
from .models import SponsorCampaign

if TYPE_CHECKING:
    from django.db.models import QuerySet


class SponsorCampaignSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[SponsorCampaign]:
        return SponsorCampaign.objects.select_related(
            "account_manager",
        ).prefetch_related("tags", "deliverables")


class CampaignDeliverableSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[CampaignDeliverable]:
        qs = CampaignDeliverable.objects.select_related(
            "campaign",
            "creator",
            "linked_session",
            "linked_publication",
        )
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(creator__user=user)
