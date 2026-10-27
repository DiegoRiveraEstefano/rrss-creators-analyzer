from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from rrss_creatos_analyzer.apps.core.choices import ChannelStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator
from .models import CreatorPersonalInfo

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class CreatorService:
    @classmethod
    @transaction.atomic
    def save_creator(
        cls,
        *,
        instance: Creator | None = None,
        personal_info_data: dict[str, Any] | None = None,
        initial_channel_data: dict[str, Any] | None = None,
        **data,
    ) -> Creator:
        creator = instance or Creator()
        is_new = creator.pk is None

        # Autogenerar slug si no se proporcionó o viene vacío
        if not data.get("slug") and data.get("handle"):
            data["slug"] = slugify(data["handle"])

        # Si es un nuevo creador y no se especificó joined_company_at, inicializar con la fecha actual
        if is_new and "joined_company_at" not in data:
            creator.joined_company_at = timezone.localdate()

        # Asignar campos al modelo
        tags = data.pop("tags", None)
        for field, value in data.items():
            setattr(creator, field, value)

        creator.save()

        if tags is not None:
            creator.tags.set(tags)

        # Si se suministran datos KYC en el mismo flujo
        if personal_info_data is not None:
            cls.save_personal_info(creator=creator, **personal_info_data)

        # Flujo ágil de onboarding: si es un nuevo creador y se incluyó canal inicial
        if is_new and initial_channel_data and initial_channel_data.get("platform"):
            platform = initial_channel_data.get("platform")
            channel_id = (
                initial_channel_data.get(
                    "platform_channel_id",
                )
                or initial_channel_data.get("handle")
                or creator.handle
            )

            ChannelService.save_channel(
                creator=creator,
                platform=platform,
                platform_channel_id=channel_id,
                handle=initial_channel_data.get("handle", creator.handle),
                channel_name=initial_channel_data.get(
                    "channel_name",
                    f"{creator.display_name} en {platform.capitalize()}",
                ),
                channel_url=initial_channel_data.get("channel_url", ""),
                is_primary=True,
                status=ChannelStatus.ACTIVE,
                followers_count=initial_channel_data.get("followers_count", 0),
                subscribers_count=initial_channel_data.get("subscribers_count", 0),
                total_views_count=initial_channel_data.get("total_views_count", 0),
            )

        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "creator_saved",
            extra={
                "creator_id": creator.id,
                "handle": creator.handle,
                "is_new": is_new,
            },
        )
        return creator

    @classmethod
    @transaction.atomic
    def save_personal_info(
        cls,
        *,
        creator: Creator,
        **personal_data,
    ) -> CreatorPersonalInfo:
        personal_info, _created = CreatorPersonalInfo.objects.get_or_create(
            creator=creator,
        )
        for field, value in personal_data.items():
            setattr(personal_info, field, value)
        personal_info.save()

        logger.info(
            "creator_personal_info_saved",
            extra={"creator_id": creator.id, "personal_info_id": personal_info.id},
        )
        return personal_info

    @classmethod
    @transaction.atomic
    def change_status(
        cls,
        *,
        creator: Creator,
        new_status: str,
        reason: str = "",
    ) -> Creator:
        if new_status not in CreatorStatus.values:
            msg = f"Estado '{new_status}' no es válido."
            raise BusinessLogicError(msg)

        old_status = creator.status
        creator.status = new_status
        if new_status in [CreatorStatus.INACTIVE, CreatorStatus.TERMINATED]:
            creator.left_company_at = timezone.localdate()
        elif new_status == CreatorStatus.ACTIVE and old_status != CreatorStatus.ACTIVE:
            creator.left_company_at = None

        if reason:
            stamp = timezone.now().strftime("%Y-%m-%d %H:%M")
            note_line = (
                f"[{stamp}] Cambio de estado {old_status} -> {new_status}: {reason}"
            )
            creator.internal_notes = (
                f"{creator.internal_notes}\n{note_line}".strip()
                if creator.internal_notes
                else note_line
            )

        creator.save(
            update_fields=[
                "status",
                "left_company_at",
                "internal_notes",
                "updated_at",
            ],
        )
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "creator_status_changed",
            extra={
                "creator_id": creator.id,
                "old_status": old_status,
                "new_status": new_status,
            },
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

        followers = data.get("followers_count", getattr(channel, "followers_count", 0))
        subscribers = data.get(
            "subscribers_count",
            getattr(channel, "subscribers_count", 0),
        )
        total_views = data.get(
            "total_views_count",
            getattr(channel, "total_views_count", 0),
        )

        if followers < 0 or subscribers < 0 or total_views < 0:
            msg = "Las métricas del canal no pueden ser valores negativos."
            raise BusinessLogicError(msg)

        creator = data.get("creator", getattr(channel, "creator", None))
        is_primary = data.get("is_primary", getattr(channel, "is_primary", False))

        # Regla de negocio: si el creador no tiene canales aún, forzar is_primary = True
        if creator and not channel.pk:
            has_channels = Channel.objects.filter(creator=creator).exists()
            if not has_channels:
                is_primary = True
                data["is_primary"] = True

        # Regla de negocio: si este canal es marcado como principal, desmarcar los demás
        if is_primary and creator:
            Channel.objects.filter(creator=creator, is_primary=True).exclude(
                pk=channel.pk or 0,
            ).update(is_primary=False)

        for field, value in data.items():
            setattr(channel, field, value)

        channel.save()
        logger.info(
            "channel_saved",
            extra={
                "channel_id": channel.id,
                "creator_id": channel.creator_id,
                "is_primary": channel.is_primary,
            },
        )
        return channel

    @classmethod
    @transaction.atomic
    def set_primary_channel(cls, *, channel: Channel) -> Channel:
        if channel.is_primary:
            return channel

        # Desmarcar los demás canales del creador
        Channel.objects.filter(creator=channel.creator, is_primary=True).exclude(
            pk=channel.pk,
        ).update(is_primary=False)

        channel.is_primary = True
        channel.save(update_fields=["is_primary", "updated_at"])
        logger.info(
            "channel_set_primary",
            extra={"channel_id": channel.id, "creator_id": channel.creator_id},
        )
        return channel

    @classmethod
    @transaction.atomic
    def toggle_sync(cls, *, channel: Channel) -> Channel:
        channel.sync_enabled = not channel.sync_enabled
        channel.save(update_fields=["sync_enabled", "updated_at"])
        logger.info(
            "channel_sync_toggled",
            extra={
                "channel_id": channel.id,
                "sync_enabled": channel.sync_enabled,
            },
        )
        return channel

    @classmethod
    @transaction.atomic
    def delete_channel(cls, *, instance: Channel) -> None:
        channel_id = instance.id
        creator = instance.creator
        was_primary = instance.is_primary
        instance.delete()

        # Si el canal eliminado era el principal, promover el siguiente disponible
        if was_primary:
            next_channel = Channel.objects.filter(creator=creator).first()
            if next_channel:
                next_channel.is_primary = True
                next_channel.save(update_fields=["is_primary", "updated_at"])

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
        followers = data.get(
            "followers_count",
            getattr(snapshot, "followers_count", 0),
        )
        subscribers = data.get(
            "subscribers_count",
            getattr(snapshot, "subscribers_count", 0),
        )
        total_views = data.get(
            "total_views_count",
            getattr(snapshot, "total_views_count", 0),
        )

        if followers < 0 or subscribers < 0 or total_views < 0:
            msg = "Las métricas de snapshot no pueden ser negativas."
            raise BusinessLogicError(msg)

        channel = data.get("channel", getattr(snapshot, "channel", None))
        snapshot_date = data.get(
            "snapshot_date", getattr(snapshot, "snapshot_date", timezone.localdate())
        )

        # Cálculo automático de deltas si no se proporcionaron explícitamente
        if channel and (
            "followers_delta" not in data or data.get("followers_delta") == 0
        ):
            prev_snapshot = (
                ChannelSnapshot.objects.filter(
                    channel=channel,
                    snapshot_date__lt=snapshot_date,
                )
                .exclude(pk=snapshot.pk or 0)
                .order_by("-snapshot_date")
                .first()
            )
            if prev_snapshot:
                data.setdefault(
                    "followers_delta", followers - prev_snapshot.followers_count
                )
                data.setdefault(
                    "subscribers_delta", subscribers - prev_snapshot.subscribers_count
                )
                data.setdefault(
                    "views_delta", total_views - prev_snapshot.total_views_count
                )

        for field, value in data.items():
            setattr(snapshot, field, value)

        snapshot.save()

        # Actualizar métricas actuales del canal con los datos del snapshot más reciente
        if channel:
            latest_date = (
                ChannelSnapshot.objects.filter(channel=channel)
                .order_by("-snapshot_date")
                .values_list("snapshot_date", flat=True)
                .first()
            )
            if latest_date == snapshot.snapshot_date:
                channel.followers_count = snapshot.followers_count
                channel.subscribers_count = snapshot.subscribers_count
                channel.paid_subscribers_count = snapshot.paid_subscribers_count
                channel.total_views_count = snapshot.total_views_count
                channel.last_synced_at = timezone.now()
                channel.save(
                    update_fields=[
                        "followers_count",
                        "subscribers_count",
                        "paid_subscribers_count",
                        "total_views_count",
                        "last_synced_at",
                        "updated_at",
                    ],
                )

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
