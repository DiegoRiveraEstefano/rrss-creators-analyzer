import logging

from django.db import transaction

from .models import CampaignDeliverable
from .models import SponsorCampaign

logger = logging.getLogger(__name__)


class SponsorCampaignService:
    @classmethod
    @transaction.atomic
    def save_campaign(
        cls,
        *,
        instance: SponsorCampaign | None = None,
        tags=None,
        **data,
    ) -> SponsorCampaign:
        campaign = instance or SponsorCampaign()
        for field, value in data.items():
            setattr(campaign, field, value)
        campaign.save()
        if tags is not None:
            campaign.tags.set(tags)
        logger.info(
            "sponsor_campaign_saved",
            extra={"campaign_id": campaign.id, "code": campaign.campaign_code},
        )
        return campaign

    @classmethod
    @transaction.atomic
    def delete_campaign(cls, *, instance: SponsorCampaign) -> None:
        cid = instance.id
        instance.delete()
        logger.info("sponsor_campaign_deleted", extra={"campaign_id": cid})


class CampaignDeliverableService:
    @classmethod
    @transaction.atomic
    def save_deliverable(
        cls,
        *,
        instance: CampaignDeliverable | None = None,
        **data,
    ) -> CampaignDeliverable:
        deliverable = instance or CampaignDeliverable()
        for field, value in data.items():
            setattr(deliverable, field, value)
        deliverable.save()
        logger.info(
            "campaign_deliverable_saved",
            extra={"deliverable_id": deliverable.id},
        )
        return deliverable

    @classmethod
    @transaction.atomic
    def delete_deliverable(cls, *, instance: CampaignDeliverable) -> None:
        did = instance.id
        instance.delete()
        logger.info("campaign_deliverable_deleted", extra={"deliverable_id": did})
