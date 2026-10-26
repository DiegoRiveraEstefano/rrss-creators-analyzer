from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Count
from django.db.models import Sum
from django.db.models.functions import Coalesce

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus

from .models import Channel
from .models import ChannelSnapshot
from .models import Creator
from .models import CreatorPersonalInfo

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CreatorSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Creator]:
        qs = (
            Creator.objects.select_related("user", "manager", "personal_info")
            .prefetch_related("tags", "channels")
            .annotate(
                channels_count=Count("channels", distinct=True),
                total_followers_count=Coalesce(
                    Sum("channels__followers_count"),
                    0,
                ),
            )
            .order_by("display_name")
        )
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(user=user)

    @classmethod
    def get_by_pk(cls, *, pk: int, user) -> Creator | None:
        qs = cls.get_visible_queryset(user=user)
        return qs.filter(pk=pk).first()

    @classmethod
    def get_kpis(cls, *, user) -> dict[str, Any]:
        base_qs = cls.get_visible_queryset(user=user)
        total = base_qs.count()
        active = base_qs.filter(status=CreatorStatus.ACTIVE).count()
        has_channels = base_qs.filter(channels__isnull=False).distinct().count()
        live_now = base_qs.filter(channels__is_live=True).distinct().count()
        return {
            "total_creators": total,
            "active_creators": active,
            "creators_with_channels": has_channels,
            "live_now_creators": live_now,
        }


class CreatorPersonalInfoSelector:
    @classmethod
    def get_for_creator(cls, *, creator_id: int, user) -> CreatorPersonalInfo | None:
        creator = CreatorSelector.get_by_pk(pk=creator_id, user=user)
        if not creator:
            return None
        return getattr(creator, "personal_info", None)


class ChannelSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Channel]:
        qs = Channel.objects.select_related("creator", "creator__manager").order_by(
            "creator__display_name",
            "platform",
        )
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(creator__user=user)

    @classmethod
    def get_for_creator(cls, *, creator_id: int, user) -> QuerySet[Channel]:
        return (
            cls.get_visible_queryset(user=user)
            .filter(creator_id=creator_id)
            .order_by("-is_primary", "platform")
        )


class ChannelSnapshotSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[ChannelSnapshot]:
        qs = ChannelSnapshot.objects.select_related(
            "channel",
            "channel__creator",
        ).order_by("-snapshot_date")
        if user.is_superuser or user.has_perm("creators.view_all_creators"):
            return qs
        return qs.filter(channel__creator__user=user)
