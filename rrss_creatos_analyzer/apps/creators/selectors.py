from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max
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
        total_audience = Channel.objects.filter(creator__in=base_qs).aggregate(
            s=Coalesce(Sum("followers_count"), 0)
        )["s"]
        return {
            "total_creators": total,
            "active_creators": active,
            "creators_with_channels": has_channels,
            "live_now_creators": live_now,
            "total_audience": total_audience,
        }

    @classmethod
    def get_360_context(cls, *, creator: Creator, user) -> dict[str, Any]:
        """Recopila el contexto 360° para la ficha integral del creador."""
        channels = ChannelSelector.get_for_creator(creator_id=creator.id, user=user)

        # Totales agregados de canales
        total_followers = sum(c.followers_count for c in channels)
        total_subscribers = sum(c.subscribers_count for c in channels)
        total_views = sum(c.total_views_count for c in channels)
        live_channels = [c for c in channels if c.is_live]

        ctx: dict[str, Any] = {
            "channels": channels,
            "total_followers": total_followers,
            "total_subscribers": total_subscribers,
            "total_views": total_views,
            "live_channels": live_channels,
            "personal_info": getattr(creator, "personal_info", None),
        }

        # Contrato vigente si la app contracts está instalada
        try:
            from rrss_creatos_analyzer.apps.contracts.models import Contract

            active_contract = (
                Contract.objects.filter(creator=creator, status="active")
                .order_by("-start_date")
                .first()
            )
            ctx["active_contract"] = active_contract
            ctx["all_contracts"] = Contract.objects.filter(creator=creator).order_by(
                "-start_date"
            )[:5]
        except ImportError, Exception:
            ctx["active_contract"] = None
            ctx["all_contracts"] = []

        # Equipo de trabajo asignado
        try:
            from rrss_creatos_analyzer.apps.members.models import CreatorTeamAssignment

            ctx["team_assignments"] = CreatorTeamAssignment.objects.filter(
                creator=creator,
            ).select_related("user", "group")
        except ImportError, Exception:
            ctx["team_assignments"] = []

        # Sesiones de streaming recientes y agregadas
        try:
            from rrss_creatos_analyzer.apps.streams.models import StreamingSession

            streams_qs = StreamingSession.objects.filter(creator=creator)
            stream_stats = streams_qs.aggregate(
                total_streams=Count("id"),
                total_hours=Coalesce(Sum("hours_streamed"), 0.0),
                avg_ccv=Coalesce(Avg("avg_ccv"), 0),
                peak_viewers=Coalesce(Max("peak_viewers"), 0),
                total_earnings=Coalesce(Sum("total_earnings"), 0.0),
            )
            ctx["stream_stats"] = stream_stats
            ctx["recent_streams"] = streams_qs.order_by("-streamed_at")[:5]
        except ImportError, Exception:
            ctx["stream_stats"] = {}
            ctx["recent_streams"] = []

        # Videos recientes
        try:
            from rrss_creatos_analyzer.apps.videos.models import Video

            videos_qs = Video.objects.filter(creator=creator)
            ctx["videos_count"] = videos_qs.count()
            ctx["recent_videos"] = videos_qs.order_by("-created_at")[:5]
        except ImportError, Exception:
            ctx["videos_count"] = 0
            ctx["recent_videos"] = []

        # Alertas de canal activas
        try:
            from rrss_creatos_analyzer.apps.alerts.models import ChannelAlert

            alerts_qs = ChannelAlert.objects.filter(creator=creator)
            ctx["active_alerts"] = alerts_qs.filter(status="active").order_by(
                "-severity", "-occurred_at"
            )
            ctx["total_active_alerts"] = ctx["active_alerts"].count()
        except ImportError, Exception:
            ctx["active_alerts"] = []
            ctx["total_active_alerts"] = 0

        # Histórico reciente de snapshots de crecimiento
        ctx["recent_snapshots"] = (
            ChannelSnapshot.objects.filter(channel__creator=creator)
            .select_related("channel")
            .order_by("-snapshot_date")[:10]
        )

        return ctx


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

    @classmethod
    def get_by_pk(cls, *, pk: int, user) -> Channel | None:
        return cls.get_visible_queryset(user=user).filter(pk=pk).first()


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

    @classmethod
    def get_for_channel(cls, *, channel_id: int, user) -> QuerySet[ChannelSnapshot]:
        return (
            cls.get_visible_queryset(user=user)
            .filter(channel_id=channel_id)
            .order_by("-snapshot_date")
        )
