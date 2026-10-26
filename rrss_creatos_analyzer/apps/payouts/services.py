import logging

from django.db import transaction

from .models import CreatorPayout

logger = logging.getLogger(__name__)


class CreatorPayoutService:
    @classmethod
    @transaction.atomic
    def save_payout(
        cls,
        *,
        instance: CreatorPayout | None = None,
        **data,
    ) -> CreatorPayout:
        payout = instance or CreatorPayout()
        for field, value in data.items():
            setattr(payout, field, value)
        payout.save()
        logger.info(
            "creator_payout_saved",
            extra={"payout_id": payout.id, "creator_id": payout.creator_id},
        )
        return payout

    @classmethod
    @transaction.atomic
    def delete_payout(cls, *, instance: CreatorPayout) -> None:
        pid = instance.id
        instance.delete()
        logger.info("creator_payout_deleted", extra={"payout_id": pid})
