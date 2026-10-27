import logging
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction

from .models import SessionSegment
from .models import StreamingSession

logger = logging.getLogger(__name__)


class StreamingSessionService:
    @classmethod
    @transaction.atomic
    def save_session(
        cls,
        *,
        instance: StreamingSession | None = None,
        tags=None,
        **data,
    ) -> StreamingSession:
        session = instance or StreamingSession()
        duration = (
            data.get("duration_seconds", getattr(session, "duration_seconds", 0)) or 0
        )
        hours = (
            (Decimal(duration) / Decimal(3600)).quantize(Decimal("0.01"))
            if duration > 0
            else Decimal("0.00")
        )
        data["hours_streamed"] = hours

        total = (
            data.get("ad_revenue", Decimal("0.00"))
            + data.get("subs_revenue", Decimal("0.00"))
            + data.get("donations_revenue", Decimal("0.00"))
            + data.get("bits_or_gifts_revenue", Decimal("0.00"))
            + data.get("sponsorship_revenue", Decimal("0.00"))
        )
        data["total_earnings"] = total
        data["earnings_per_hour"] = (
            (total / hours).quantize(Decimal("0.01")) if hours > 0 else Decimal("0.00")
        )

        for field, value in data.items():
            setattr(session, field, value)
        session.save()
        if tags is not None:
            session.tags.set(tags)

        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info(
            "streaming_session_saved",
            extra={
                "session_id": session.id,
                "creator_id": session.creator_id,
                "platform": session.platform,
            },
        )
        return session

    @classmethod
    @transaction.atomic
    def delete_session(cls, *, instance: StreamingSession) -> None:
        session_id = instance.id
        instance.delete()
        transaction.on_commit(
            lambda: cache.delete("analytics:creator_performance_summary:v1"),
        )
        logger.info("streaming_session_deleted", extra={"session_id": session_id})


class SessionSegmentService:
    @classmethod
    @transaction.atomic
    def save_segment(
        cls,
        *,
        instance: SessionSegment | None = None,
        **data,
    ) -> SessionSegment:
        segment = instance or SessionSegment()
        for field, value in data.items():
            setattr(segment, field, value)
        segment.save()
        logger.info(
            "session_segment_saved",
            extra={"segment_id": segment.id, "session_id": segment.session_id},
        )
        return segment

    @classmethod
    @transaction.atomic
    def delete_segment(cls, *, instance: SessionSegment) -> None:
        segment_id = instance.id
        instance.delete()
        logger.info("session_segment_deleted", extra={"segment_id": segment_id})
