from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Sum

from .models import Video
from .models import VideoPublication
from .models import VideoRelation

if TYPE_CHECKING:
    from django.db.models import QuerySet


class VideoSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[Video]:
        qs = Video.objects.select_related(
            "creator",
            "assigned_editor",
        ).prefetch_related("tags", "publications")
        if user.is_superuser or user.has_perm("videos.view_all_videos"):
            return qs
        return qs.filter(creator__user=user)

    @classmethod
    def get_profitability_audit(
        cls,
        *,
        user,
        creator_id: int | None = None,
        content_format: str | None = None,
        start_date=None,
        end_date=None,
    ) -> list[dict[str, Any]]:
        qs = cls.get_visible_queryset(user=user)
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        if content_format:
            qs = qs.filter(content_format=content_format)
        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        results = []
        for video in qs:
            tot_rev = video.publications.aggregate(tot=Sum("estimated_revenue"))[
                "tot"
            ] or Decimal("0.00")
            profit = tot_rev - video.total_production_cost
            cost = video.total_production_cost
            if cost > Decimal("0.00"):
                roi = ((tot_rev - cost) / cost) * Decimal("100.0")
                roi = roi.quantize(Decimal("0.01"))
            else:
                roi = None

            if roi is None:
                category = "N/A"
            elif roi > Decimal("0.00"):
                category = "Rentable"
            elif roi == Decimal("0.00"):
                category = "Equilibrio"
            else:
                category = "Deficitario"

            results.append(
                {
                    "video": video,
                    "production_cost": cost,
                    "estimated_revenue": tot_rev,
                    "net_profit": profit,
                    "roi_percentage": roi,
                    "profit_category": category,
                },
            )
        return results


class VideoPublicationSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[VideoPublication]:
        qs = VideoPublication.objects.select_related(
            "video",
            "creator",
            "channel",
            "import_batch",
        )
        if user.is_superuser or user.has_perm("videos.view_all_videos"):
            return qs
        return qs.filter(creator__user=user)


class VideoRelationSelector:
    @classmethod
    def get_visible_queryset(cls, *, user) -> QuerySet[VideoRelation]:
        qs = VideoRelation.objects.select_related(
            "source_video",
            "target_video",
            "target_session",
        )
        if user.is_superuser or user.has_perm("videos.view_all_videos"):
            return qs
        return qs.filter(source_video__creator__user=user)
