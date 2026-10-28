from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db import transaction

from rrss_creatos_analyzer.apps.core.choices import DeliverableStatus
from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError

from .models import Video
from .models import VideoPublication
from .models import VideoRelation

if TYPE_CHECKING:
    from rrss_creatos_analyzer.apps.campaigns.models import CampaignDeliverable

logger = logging.getLogger(__name__)


class VideoService:
    @classmethod
    @transaction.atomic
    def save_video(
        cls,
        *,
        instance: Video | None = None,
        tags=None,
        **data,
    ) -> Video:
        video = instance or Video()

        prod_cost = data.get(
            "production_cost",
            getattr(video, "production_cost", Decimal("0.00")),
        ) or Decimal("0.00")
        edit_cost = data.get(
            "editing_cost",
            getattr(video, "editing_cost", Decimal("0.00")),
        ) or Decimal("0.00")
        thumb_cost = data.get(
            "thumbnail_cost",
            getattr(video, "thumbnail_cost", Decimal("0.00")),
        ) or Decimal("0.00")

        if any(c < Decimal("0.00") for c in (prod_cost, edit_cost, thumb_cost)):
            msg = "Los costos de producción del video no pueden ser negativos."
            raise BusinessLogicError(msg)

        data["production_cost"] = prod_cost
        data["editing_cost"] = edit_cost
        data["thumbnail_cost"] = thumb_cost
        data["total_production_cost"] = prod_cost + edit_cost + thumb_cost

        status = data.get("status", getattr(video, "status", VideoStatus.IDEA))
        if status == VideoStatus.PUBLISHED:
            if instance and instance.pk:
                has_published = instance.publications.filter(
                    status=PublicationStatus.PUBLISHED,
                ).exists()
                if not has_published:
                    msg = (
                        "Un video no puede marcarse en estado 'published' "
                        "a menos que exista al menos una publicación vinculada "
                        "en estado 'published'."
                    )
                    raise BusinessLogicError(msg)
            else:
                msg = (
                    "Un nuevo video no puede crearse directamente en estado "
                    "'published' sin publicaciones vinculadas."
                )
                raise BusinessLogicError(msg)

        for field, value in data.items():
            setattr(video, field, value)
        video.save()
        if tags is not None:
            video.tags.set(tags)

        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "video_saved",
            extra={"video_id": video.id, "creator_id": video.creator_id},
        )
        return video

    @classmethod
    @transaction.atomic
    def delete_video(cls, *, instance: Video) -> None:
        video_id = instance.id
        instance.delete()
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info("video_deleted", extra={"video_id": video_id})


class VideoPublicationService:
    @classmethod
    @transaction.atomic
    def save_publication(
        cls,
        *,
        instance: VideoPublication | None = None,
        deliverable: CampaignDeliverable | None = None,
        **data,
    ) -> VideoPublication:
        pub = instance or VideoPublication()
        views = data.get("views_count", getattr(pub, "views_count", 0)) or 0
        est_rev = data.get("estimated_revenue", getattr(pub, "estimated_revenue", None))
        if est_rev is None or est_rev == Decimal("0.00"):
            ad_rev = data.get(
                "ad_revenue",
                getattr(pub, "ad_revenue", Decimal("0.00")),
            ) or Decimal("0.00")
            sp_rev = data.get(
                "sponsorship_revenue",
                getattr(pub, "sponsorship_revenue", Decimal("0.00")),
            ) or Decimal("0.00")
            est_rev = ad_rev + sp_rev
            data["estimated_revenue"] = est_rev

        data["rpm_estimated"] = (
            (est_rev / (Decimal(views) / Decimal(1000))).quantize(Decimal("0.01"))
            if views > 0
            else Decimal("0.00")
        )

        likes = data.get("likes_count", getattr(pub, "likes_count", 0)) or 0
        comments = data.get("comments_count", getattr(pub, "comments_count", 0)) or 0
        shares = data.get("shares_count", getattr(pub, "shares_count", 0)) or 0
        saves = data.get("saves_count", getattr(pub, "saves_count", 0)) or 0
        if views > 0:
            interactions = likes + comments + shares + saves
            data["engagement_rate"] = (
                (Decimal(interactions) / Decimal(views)) * Decimal("100.0")
            ).quantize(Decimal("0.01"))
        else:
            data["engagement_rate"] = Decimal("0.00")

        for field, value in data.items():
            setattr(pub, field, value)
        pub.save()

        # RN-VID-002 / CU-VID-04: Auto-advance parent Video if ready
        if (
            pub.status == PublicationStatus.PUBLISHED
            and pub.video
            and pub.video.status == VideoStatus.READY
        ):
            pub.video.status = VideoStatus.PUBLISHED
            pub.video.save()

        if deliverable:
            deliverable.linked_publication = pub
            deliverable.status = DeliverableStatus.PUBLISHED
            deliverable.save()

        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "video_publication_saved",
            extra={"publication_id": pub.id, "video_id": pub.video_id},
        )
        return pub

    @classmethod
    @transaction.atomic
    def delete_publication(cls, *, instance: VideoPublication) -> None:
        pub_id = instance.id
        instance.delete()
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info("video_publication_deleted", extra={"publication_id": pub_id})


class VideoRelationService:
    @classmethod
    @transaction.atomic
    def save_relation(
        cls,
        *,
        instance: VideoRelation | None = None,
        **data,
    ) -> VideoRelation:
        rel = instance or VideoRelation()

        source_video = data.get(
            "source_video",
            getattr(rel, "source_video", None),
        )
        target_video = data.get(
            "target_video",
            getattr(rel, "target_video", None),
        )
        target_session = data.get(
            "target_session",
            getattr(rel, "target_session", None),
        )

        if not target_video and not target_session:
            msg = (
                "Debe seleccionar al menos un Video Relacionado "
                "o una Sesión de Streaming."
            )
            raise BusinessLogicError(msg)

        if source_video and target_video and source_video == target_video:
            msg = "Un video no puede tener una relación consigo mismo."
            raise BusinessLogicError(msg)

        rtype = data.get("relation_type", getattr(rel, "relation_type", None))
        if target_video and rtype:
            existing = VideoRelation.objects.filter(
                source_video=source_video,
                target_video=target_video,
                relation_type=rtype,
            )
            if rel.pk:
                existing = existing.exclude(pk=rel.pk)
            if existing.exists():
                msg = "Ya existe una relación con el mismo tipo entre ambos videos."
                raise BusinessLogicError(msg)

        for field, value in data.items():
            setattr(rel, field, value)
        rel.save()
        logger.info(
            "video_relation_saved",
            extra={"relation_id": rel.id, "source_video_id": rel.source_video_id},
        )
        return rel

    @classmethod
    @transaction.atomic
    def delete_relation(cls, *, instance: VideoRelation) -> None:
        rel_id = instance.id
        instance.delete()
        logger.info("video_relation_deleted", extra={"relation_id": rel_id})
