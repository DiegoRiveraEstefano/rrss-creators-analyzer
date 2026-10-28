from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db import models
from django.db import transaction

from rrss_creatos_analyzer.apps.core.choices import DeliverableStatus
from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError

from .models import SessionSegment
from .models import StreamingSession

if TYPE_CHECKING:
    from rrss_creatos_analyzer.apps.campaigns.models import CampaignDeliverable

logger = logging.getLogger(__name__)


class StreamingSessionService:
    @classmethod
    @transaction.atomic
    def save_session(  # noqa: C901
        cls,
        *,
        instance: StreamingSession | None = None,
        tags=None,
        deliverable: CampaignDeliverable | None = None,
        **data,
    ) -> StreamingSession:
        session = instance or StreamingSession()

        streamed_at = data.get(
            "streamed_at",
            getattr(session, "streamed_at", None),
        )
        ended_at = data.get("ended_at", getattr(session, "ended_at", None))
        if streamed_at and ended_at:
            if ended_at < streamed_at:
                msg = (
                    "La fecha/hora de fin no puede ser anterior "
                    "a la fecha/hora de inicio del stream."
                )
                raise BusinessLogicError(msg)
            if not data.get("duration_seconds") and not getattr(
                session,
                "duration_seconds",
                0,
            ):
                data["duration_seconds"] = int((ended_at - streamed_at).total_seconds())

        duration = (
            data.get("duration_seconds", getattr(session, "duration_seconds", 0)) or 0
        )
        if duration < 0:
            msg = "La duración en segundos no puede ser negativa."
            raise BusinessLogicError(msg)

        hours = (
            (Decimal(duration) / Decimal(3600)).quantize(Decimal("0.01"))
            if duration > 0
            else Decimal("0.00")
        )
        data["hours_streamed"] = hours

        peak = data.get("peak_viewers", getattr(session, "peak_viewers", 0)) or 0
        avg = data.get("avg_ccv", getattr(session, "avg_ccv", 0)) or 0
        if avg > peak:
            msg = (
                "El pico de espectadores (peak_viewers) debe ser mayor o igual "
                "a la media de espectadores concurrentes (avg_ccv)."
            )
            raise BusinessLogicError(msg)

        ad = data.get(
            "ad_revenue",
            getattr(session, "ad_revenue", Decimal("0.00")),
        ) or Decimal("0.00")
        subs = data.get(
            "subs_revenue",
            getattr(session, "subs_revenue", Decimal("0.00")),
        ) or Decimal("0.00")
        donations = data.get(
            "donations_revenue",
            getattr(session, "donations_revenue", Decimal("0.00")),
        ) or Decimal("0.00")
        bits = data.get(
            "bits_or_gifts_revenue",
            getattr(session, "bits_or_gifts_revenue", Decimal("0.00")),
        ) or Decimal("0.00")
        sponsor = data.get(
            "sponsorship_revenue",
            getattr(session, "sponsorship_revenue", Decimal("0.00")),
        ) or Decimal("0.00")

        if any(v < Decimal("0.00") for v in (ad, subs, donations, bits, sponsor)):
            msg = "Los componentes de ingresos del stream no pueden ser negativos."
            raise BusinessLogicError(msg)

        is_sponsored = data.get(
            "is_sponsored",
            getattr(session, "is_sponsored", False),
        )
        if is_sponsored and sponsor <= Decimal("0.00"):
            msg = (
                "Una sesión marcada como patrocinada debe contar con "
                "un ingreso de patrocinio mayor a cero."
            )
            raise BusinessLogicError(msg)

        total = ad + subs + donations + bits + sponsor
        data["ad_revenue"] = ad
        data["subs_revenue"] = subs
        data["donations_revenue"] = donations
        data["bits_or_gifts_revenue"] = bits
        data["sponsorship_revenue"] = sponsor
        data["total_earnings"] = total
        data["earnings_per_hour"] = (
            (total / hours).quantize(Decimal("0.01")) if hours > 0 else Decimal("0.00")
        )

        for field, value in data.items():
            setattr(session, field, value)
        session.save()
        if tags is not None:
            session.tags.set(tags)

        if deliverable:
            deliverable.linked_session = session
            deliverable.status = DeliverableStatus.PUBLISHED
            deliverable.save()

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
    def upsert_session(
        cls,
        *,
        creator,
        platform: str,
        external_stream_id: str = "",
        **data,
    ) -> tuple[StreamingSession, bool]:
        session = None
        created = False
        if external_stream_id:
            session = StreamingSession.objects.filter(
                creator=creator,
                platform=platform,
                external_stream_id=external_stream_id,
            ).first()

        if not session:
            session = StreamingSession(
                creator=creator,
                platform=platform,
                external_stream_id=external_stream_id,
            )
            created = True

        data["creator"] = creator
        data["platform"] = platform
        data["external_stream_id"] = external_stream_id
        saved = cls.save_session(instance=session, **data)
        return saved, created

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

        session = data.get("session", getattr(segment, "session", None))
        start_offset = (
            data.get(
                "start_offset_seconds",
                getattr(segment, "start_offset_seconds", 0),
            )
            or 0
        )
        duration = (
            data.get("duration_seconds", getattr(segment, "duration_seconds", 0)) or 0
        )
        avg = data.get("avg_ccv", getattr(segment, "avg_ccv", 0)) or 0
        peak = data.get("peak_viewers", getattr(segment, "peak_viewers", 0)) or 0

        if avg > peak:
            msg = (
                "El pico de espectadores debe ser mayor o igual "
                "al promedio de CCV del segmento."
            )
            raise BusinessLogicError(msg)

        if session and session.duration_seconds > 0:
            if start_offset + duration > session.duration_seconds:
                msg = (
                    "El rango del segmento no puede exceder "
                    "la duración total del stream."
                )
                raise BusinessLogicError(msg)

            other_segs = session.segments.all()
            if segment.pk:
                other_segs = other_segs.exclude(pk=segment.pk)
            segs_dur = (
                other_segs.aggregate(tot=models.Sum("duration_seconds"))["tot"] or 0
            )
            if segs_dur + duration > session.duration_seconds:
                msg = (
                    "La suma de duraciones de los segmentos no puede superar "
                    "la duración total del stream."
                )
                raise BusinessLogicError(msg)

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
