import logging
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError

from .models import Video
from .models import VideoPublication
from .models import VideoRelation

logger = logging.getLogger(__name__)


class VideoService:
    @classmethod
    @transaction.atomic
    def save_video(cls, *, instance: Video | None = None, tags=None, **data) -> Video:
        video = instance or Video()
        total_cost = (
            data.get("production_cost", Decimal("0.00"))
            + data.get("editing_cost", Decimal("0.00"))
            + data.get("thumbnail_cost", Decimal("0.00"))
        )
        data["total_production_cost"] = total_cost
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
        **data,
    ) -> VideoPublication:
        pub = instance or VideoPublication()
        views = data.get("views_count", getattr(pub, "views_count", 0)) or 0
        est_rev = data.get("estimated_revenue", Decimal("0.00"))
        if not est_rev:
            est_rev = data.get("ad_revenue", Decimal("0.00")) + data.get(
                "sponsorship_revenue",
                Decimal("0.00"),
            )
            data["estimated_revenue"] = est_rev

        data["rpm_estimated"] = (
            (est_rev / (Decimal(views) / Decimal(1000))).quantize(Decimal("0.01"))
            if views > 0
            else Decimal("0.00")
        )

        for field, value in data.items():
            setattr(pub, field, value)
        pub.save()

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
        if not data.get("target_video") and not data.get("target_session"):
            msg = (
                "Debe seleccionar al menos un Video Relacionado "
                "o una Sesión de Streaming."
            )
            raise BusinessLogicError(msg)

        rel = instance or VideoRelation()
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
