import logging

from django.core.cache import cache
from django.db import transaction
from slugify import slugify

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator

logger = logging.getLogger(__name__)


class CreatorService:
    @classmethod
    @transaction.atomic
    def save_creator(
        cls,
        *,
        instance: Creator | None = None,
        tags=None,
        **data,
    ) -> Creator:
        creator = instance or Creator()
        if not data.get("slug") and data.get("handle"):
            data["slug"] = slugify(data["handle"])
        for field, value in data.items():
            setattr(creator, field, value)
        creator.save()
        if tags is not None:
            creator.tags.set(tags)
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "creator_saved",
            extra={"creator_id": creator.id, "handle": creator.handle},
        )
        return creator

    @classmethod
    @transaction.atomic
    def delete_creator(cls, *, instance: Creator) -> None:
        creator_id = instance.id
        instance.delete()
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info("creator_deleted", extra={"creator_id": creator_id})


class ChannelService:
    @classmethod
    @transaction.atomic
    def save_channel(cls, *, instance: Channel | None = None, **data) -> Channel:
        channel = instance or Channel()
        for field, value in data.items():
            setattr(channel, field, value)
        channel.save()
        logger.info(
            "channel_saved",
            extra={"channel_id": channel.id, "creator_id": channel.creator_id},
        )
        return channel

    @classmethod
    @transaction.atomic
    def delete_channel(cls, *, instance: Channel) -> None:
        channel_id = instance.id
        instance.delete()
        logger.info("channel_deleted", extra={"channel_id": channel_id})


class ChannelSnapshotService:
    @classmethod
    @transaction.atomic
    def save_snapshot(
        cls,
        *,
        instance: ChannelSnapshot | None = None,
        **data,
    ) -> ChannelSnapshot:
        snapshot = instance or ChannelSnapshot()
        for field, value in data.items():
            setattr(snapshot, field, value)
        snapshot.save()
        logger.info(
            "channel_snapshot_saved",
            extra={"snapshot_id": snapshot.id, "channel_id": snapshot.channel_id},
        )
        return snapshot

    @classmethod
    @transaction.atomic
    def delete_snapshot(cls, *, instance: ChannelSnapshot) -> None:
        snapshot_id = instance.id
        instance.delete()
        logger.info("channel_snapshot_deleted", extra={"snapshot_id": snapshot_id})
