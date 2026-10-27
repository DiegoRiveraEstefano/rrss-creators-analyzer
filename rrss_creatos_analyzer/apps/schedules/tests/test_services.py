from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal

import pytest

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.schedules.choices import DayOfWeek
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.services import ScheduleService
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorScheduleSlotFactory,
)
from rrss_creatos_analyzer.apps.streams.models import StreamingSession

pytestmark = pytest.mark.django_db


class TestPatternService:
    def test_save_weekly_schedule_success(self):
        creator = CreatorFactory()
        schedule = ScheduleService.save_weekly_schedule(
            creator_id=creator.id,
            day_of_week=DayOfWeek.WEDNESDAY,
            start_time=time(19, 0),
            end_time=time(23, 0),
            planned_duration_minutes=240,
            effective_from=date(2026, 10, 1),
        )
        assert schedule.pk is not None
        assert schedule.planned_duration_minutes == 240  # noqa: PLR2004

    def test_save_weekly_schedule_end_before_start_raises_error(self):
        creator = CreatorFactory()
        with pytest.raises(BusinessLogicError, match="anterior a la de inicio"):
            ScheduleService.save_weekly_schedule(
                creator_id=creator.id,
                day_of_week=DayOfWeek.MONDAY,
                start_time=time(20, 0),
                end_time=time(18, 0),
                planned_duration_minutes=120,
                effective_from=date(2026, 10, 1),
                effective_until=date(2026, 9, 1),
            )

    def test_save_weekly_schedule_overlap_raises_error(self):
        creator = CreatorFactory()
        ScheduleService.save_weekly_schedule(
            creator_id=creator.id,
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(14, 0),
            end_time=time(18, 0),
            planned_duration_minutes=240,
            effective_from=date(2026, 10, 1),
        )

        with pytest.raises(BusinessLogicError, match="superposición horaria"):
            ScheduleService.save_weekly_schedule(
                creator_id=creator.id,
                day_of_week=DayOfWeek.MONDAY,
                start_time=time(16, 0),
                end_time=time(20, 0),
                planned_duration_minutes=240,
                effective_from=date(2026, 10, 1),
            )

    def test_generate_slots_for_period_idempotent(self):
        creator = CreatorFactory()
        # Patrón para los viernes (Friday = 5)
        ScheduleService.save_weekly_schedule(
            creator_id=creator.id,
            day_of_week=DayOfWeek.FRIDAY,
            start_time=time(16, 0),
            end_time=time(20, 0),
            planned_duration_minutes=240,
            effective_from=date(2026, 10, 1),
        )

        # Rango con dos viernes: 2026-10-02 y 2026-10-09
        start = date(2026, 10, 1)
        end = date(2026, 10, 10)

        count = ScheduleService.generate_slots_for_period(
            start_date=start,
            end_date=end,
            creator_id=creator.id,
        )
        assert count == 2  # noqa: PLR2004

        # Segunda ejecución: debe ser idempotente y crear 0
        count_repeat = ScheduleService.generate_slots_for_period(
            start_date=start,
            end_date=end,
            creator_id=creator.id,
        )
        assert count_repeat == 0

    def test_save_schedule_pattern_with_rrule_multi_day(self):
        creator = CreatorFactory()
        pattern = ScheduleService.save_schedule_pattern(
            creator_id=creator.id,
            rrule="FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1",
            title="Streams Lunes Miércoles y Viernes",
            start_time=time(18, 0),
            end_time=time(22, 0),
            planned_duration_minutes=240,
            effective_from=date(2026, 10, 1),
        )
        assert pattern.pk is not None
        assert "Lunes, Miércoles y Viernes" in pattern.human_recurrence

        # Genera para 2026-10-01 al 2026-10-10:
        # 2026-10-02 (Vie), 2026-10-05 (Lun), 2026-10-07 (Mié), 2026-10-09 (Vie)
        # Total: 4 slots
        count = ScheduleService.generate_slots_for_period(
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 10),
            creator_id=creator.id,
        )
        assert count == 4  # noqa: PLR2004


class TestReconciliationService:
    def test_reconcile_slot_completed_on_time(self):
        creator = CreatorFactory()
        slot = CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 20),
            scheduled_start_time=time(18, 0),
            scheduled_end_time=time(22, 0),
            planned_hours=Decimal("4.00"),
        )
        # Transmisión real: inicia a las 18:05 (dentro de tolerancia) y dura 4.0 horas
        stream_dt = datetime(2026, 10, 20, 18, 5, tzinfo=UTC)
        session = StreamingSession.objects.create(
            creator=creator,
            session_title="Stream en Vivo",
            game_or_category="Just Chatting",
            streamed_at=stream_dt,
            ended_at=stream_dt + timedelta(hours=4),
            duration_seconds=14400,
            hours_streamed=Decimal("4.00"),
        )

        reconciled = ScheduleService.reconcile_slot(slot=slot)
        assert reconciled.status == ScheduleSlotStatus.COMPLETED
        assert reconciled.actual_streaming_session == session
        assert reconciled.start_delay_minutes == 5  # noqa: PLR2004
        assert reconciled.compliance_rate_pct == Decimal("100.00")

    def test_reconcile_slot_late_start(self):
        creator = CreatorFactory()
        slot = CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 21),
            scheduled_start_time=time(18, 0),
            scheduled_end_time=time(22, 0),
            planned_hours=Decimal("4.00"),
        )
        # Inicia a las 18:35 (35 min tarde > 15 min grace period)
        stream_dt = datetime(2026, 10, 21, 18, 35, tzinfo=UTC)
        StreamingSession.objects.create(
            creator=creator,
            session_title="Stream Tarde",
            game_or_category="Just Chatting",
            streamed_at=stream_dt,
            ended_at=stream_dt + timedelta(hours=4),
            duration_seconds=14400,
            hours_streamed=Decimal("4.00"),
        )

        reconciled = ScheduleService.reconcile_slot(slot=slot)
        assert reconciled.status == ScheduleSlotStatus.LATE
        assert reconciled.start_delay_minutes == 35  # noqa: PLR2004
        assert reconciled.compliance_rate_pct == Decimal("100.00")

    def test_reconcile_slot_partial_stream(self):
        creator = CreatorFactory()
        slot = CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 22),
            scheduled_start_time=time(18, 0),
            scheduled_end_time=time(22, 0),
            planned_hours=Decimal("4.00"),
        )
        # Transmite solo 1.5 horas (37.5% < 90% threshold)
        stream_dt = datetime(2026, 10, 22, 18, 0, tzinfo=UTC)
        StreamingSession.objects.create(
            creator=creator,
            session_title="Stream Corto",
            game_or_category="Just Chatting",
            streamed_at=stream_dt,
            ended_at=stream_dt + timedelta(minutes=90),
            duration_seconds=5400,
            hours_streamed=Decimal("1.50"),
        )

        reconciled = ScheduleService.reconcile_slot(slot=slot)
        assert reconciled.status == ScheduleSlotStatus.PARTIAL
        assert reconciled.compliance_rate_pct == Decimal("37.50")

    def test_reconcile_slot_missed(self):
        creator = CreatorFactory()
        slot = CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 23),
            scheduled_start_time=time(18, 0),
            scheduled_end_time=time(22, 0),
            planned_hours=Decimal("4.00"),
        )
        reconciled = ScheduleService.reconcile_slot(slot=slot)
        assert reconciled.status == ScheduleSlotStatus.MISSED
        assert reconciled.actual_hours == Decimal("0.00")


class TestComplianceService:
    def test_create_and_approve_exception_marks_slot_justified(self):
        creator = CreatorFactory()
        slot = CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 25),
            status=ScheduleSlotStatus.MISSED,
        )

        exc = ScheduleService.register_exception(
            creator_id=creator.id,
            start_date=date(2026, 10, 25),
            end_date=date(2026, 10, 25),
            reason_type=ScheduleExceptionReason.MEDICAL,
            title="Licencia médica",
            description="Certificado médico adjunto",
        )
        assert exc.is_approved is False

        # Al aprobar, los slots correspondientes pasan a JUSTIFIED_ABSENCE
        approved_exc = ScheduleService.approve_exception(
            exception_id=exc.id,
            approved_by=None,
        )
        assert approved_exc.is_approved is True
        slot.refresh_from_db()
        assert slot.status == ScheduleSlotStatus.JUSTIFIED_ABSENCE

    def test_calculate_monthly_compliance_summary(self):
        creator = CreatorFactory()
        # Slot 1: Completado (4 horas)
        CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 5),
            planned_hours=Decimal("4.00"),
            actual_hours=Decimal("4.00"),
            status=ScheduleSlotStatus.COMPLETED,
        )
        # Slot 2: Completado (4 horas)
        CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 12),
            planned_hours=Decimal("4.00"),
            actual_hours=Decimal("4.00"),
            status=ScheduleSlotStatus.COMPLETED,
        )
        # Slot 3: Falta justificada (4 horas)
        CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 19),
            planned_hours=Decimal("4.00"),
            actual_hours=Decimal("0.00"),
            status=ScheduleSlotStatus.JUSTIFIED_ABSENCE,
        )

        summary = ScheduleService.calculate_monthly_compliance_summary(
            creator_id=creator.id,
            year=2026,
            month=10,
        )
        assert summary.stipulated_days_count == 3  # noqa: PLR2004
        assert summary.completed_days_count == 2  # noqa: PLR2004
        assert summary.justified_days_count == 1
        assert summary.actual_hours == Decimal("8.00")
        # Días netos = 3 - 1 = 2; completados = 2 -> 100%
        assert summary.days_compliance_rate_pct == Decimal("100.00")
        assert summary.is_compliant is True
