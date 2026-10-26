import logging

from django.db import transaction

from .models import ChannelAlert

logger = logging.getLogger(__name__)


class ChannelAlertService:
    @classmethod
    @transaction.atomic
    def save_alert(
        cls,
        *,
        instance: ChannelAlert | None = None,
        **data,
    ) -> ChannelAlert:
        alert = instance or ChannelAlert()
        for field, value in data.items():
            setattr(alert, field, value)
        alert.save()
        logger.info(
            "channel_alert_saved",
            extra={
                "alert_id": alert.id,
                "creator_id": alert.creator_id,
                "severity": alert.severity,
            },
        )
        return alert

    @classmethod
    @transaction.atomic
    def delete_alert(cls, *, instance: ChannelAlert) -> None:
        alert_id = instance.id
        instance.delete()
        logger.info("channel_alert_deleted", extra={"alert_id": alert_id})
