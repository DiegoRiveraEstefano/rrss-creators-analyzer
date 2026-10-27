import logging
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException
from rrss_creatos_analyzer.apps.streams.models import StreamingSession

logger = logging.getLogger(__name__)


class ReconciliationService:
    """Motor de conciliación entre citas de agenda y transmisiones en vivo reales."""

    GRACE_PERIOD_MINUTES = 15
    RECONCILIATION_WINDOW_MINUTES = 120
    COMPLETION_THRESHOLD_PCT = Decimal("90.00")

    @classmethod
    @transaction.atomic
    def reconcile_slot(  # noqa: PLR0912
        cls,
        *,
        slot: CreatorScheduleSlot,
        streaming_session: StreamingSession | None = None,
    ) -> CreatorScheduleSlot:
        """Concilia un slot individual con una sesión real o búsqueda candidata."""
        session = streaming_session
        if not session and slot.status not in {
            ScheduleSlotStatus.JUSTIFIED_ABSENCE,
            ScheduleSlotStatus.CANCELLED,
        }:
            dt_scheduled_start = datetime.combine(
                slot.scheduled_date, slot.scheduled_start_time,
            )
            if timezone.is_naive(dt_scheduled_start):
                dt_scheduled_start = timezone.make_aware(
                    dt_scheduled_start, timezone.get_current_timezone(),
                )

            window_start = dt_scheduled_start - timedelta(
                minutes=cls.RECONCILIATION_WINDOW_MINUTES,
            )
            window_end = dt_scheduled_start + timedelta(
                minutes=cls.RECONCILIATION_WINDOW_MINUTES,
            )

            candidate_qs = StreamingSession.objects.filter(
                creator_id=slot.creator_id,
                streamed_at__gte=window_start,
                streamed_at__lte=window_end,
            ).order_by("streamed_at")

            if slot.channel_id:
                candidate_qs = candidate_qs.filter(channel_id=slot.channel_id)

            session = candidate_qs.first()

        if session:
            slot.actual_streaming_session = session
            slot.actual_start_datetime = session.streamed_at
            slot.actual_end_datetime = session.ended_at
            slot.actual_duration_minutes = session.duration_seconds // 60
            slot.actual_hours = session.hours_streamed

            scheduled_naive = datetime.combine(
                slot.scheduled_date, slot.scheduled_start_time,
            )
            if timezone.is_aware(session.streamed_at):
                actual_naive = timezone.localtime(session.streamed_at).replace(
                    tzinfo=None,
                )
            else:
                actual_naive = session.streamed_at

            delay_seconds = (actual_naive - scheduled_naive).total_seconds()
            slot.start_delay_minutes = int(delay_seconds // 60)

            if slot.planned_hours > Decimal("0.00"):
                rate = (slot.actual_hours / slot.planned_hours) * Decimal("100.00")
                slot.compliance_rate_pct = min(
                    Decimal("100.00"), rate.quantize(Decimal("0.01")),
                )
            else:
                slot.compliance_rate_pct = Decimal("100.00")

            is_duration_fulfilled = (
                slot.compliance_rate_pct >= cls.COMPLETION_THRESHOLD_PCT
            )
            is_punctual = slot.start_delay_minutes <= cls.GRACE_PERIOD_MINUTES

            if is_duration_fulfilled:
                slot.status = (
                    ScheduleSlotStatus.COMPLETED
                    if is_punctual
                    else ScheduleSlotStatus.LATE
                )
            elif slot.actual_hours > Decimal("0.00"):
                slot.status = ScheduleSlotStatus.PARTIAL
            else:
                slot.status = ScheduleSlotStatus.MISSED
        else:
            today = timezone.localdate()
            if slot.scheduled_date < today:
                has_exception = ScheduleException.objects.filter(
                    creator_id=slot.creator_id,
                    is_approved=True,
                    start_date__lte=slot.scheduled_date,
                    end_date__gte=slot.scheduled_date,
                ).exists()

                slot.status = (
                    ScheduleSlotStatus.JUSTIFIED_ABSENCE
                    if has_exception
                    else ScheduleSlotStatus.MISSED
                )
                slot.compliance_rate_pct = Decimal("0.00")
                slot.actual_hours = Decimal("0.00")

        slot.save()
        logger.info(
            "schedule_slot_reconciled",
            extra={
                "slot_id": slot.id,
                "status": slot.status,
                "session_id": session.id if session else None,
            },
        )
        return slot

    @classmethod
    @transaction.atomic
    def reconcile_creator_period(
        cls,
        *,
        start_date: date,
        end_date: date,
        creator_id: int | None = None,
    ) -> int:
        """Concilia masivamente los slots programados dentro de un rango de fechas."""
        slots_qs = CreatorScheduleSlot.objects.filter(
            scheduled_date__gte=start_date,
            scheduled_date__lte=end_date,
        )
        if creator_id:
            slots_qs = slots_qs.filter(creator_id=creator_id)

        count = 0
        for slot in slots_qs:
            cls.reconcile_slot(slot=slot)
            count += 1
        return count
