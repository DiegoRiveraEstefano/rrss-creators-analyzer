from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max
from django.db.models import Sum

from .models import SessionSegment
from .models import StreamingSession

if TYPE_CHECKING:
    from django.db.models import QuerySet


class StreamingSessionSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[StreamingSession]:
        qs = StreamingSession.objects.select_related(
            "creator",
            "channel",
            "import_batch",
        ).prefetch_related("tags")
        if user.is_superuser or user.has_perm("streams.view_all_sessions"):
            return qs
        return qs.filter(creator__user=user)

    @classmethod
    def get_category_performance_stats(
        cls,
        *,
        user,
        creator_id: int | None = None,
        platform: str | None = None,
        start_date=None,
        end_date=None,
    ) -> list[dict[str, Any]]:
        qs = cls.get_visible_queryset(user=user)
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        if platform:
            qs = qs.filter(platform=platform)
        if start_date:
            qs = qs.filter(streamed_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(streamed_at__date__lte=end_date)

        aggregated = (
            qs.values("game_or_category")
            .annotate(
                total_sessions=Count("id"),
                total_hours=Sum("hours_streamed"),
                avg_ccv=Avg("avg_ccv"),
                peak_viewers=Max("peak_viewers"),
                total_earnings=Sum("total_earnings"),
            )
            .order_by("-avg_ccv")
        )
        return list(aggregated)


class SessionSegmentSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[SessionSegment]:
        qs = SessionSegment.objects.select_related("session", "session__creator")
        if user.is_superuser or user.has_perm("streams.view_all_sessions"):
            return qs
        return qs.filter(session__creator__user=user)
