import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException

logger = logging.getLogger(__name__)


class ComplianceService:
    """Auditoría, permisos y consolidación mensual de cumplimiento contractual."""

    GRACE_PERIOD_MINUTES = 15
    COMPLETION_THRESHOLD_PCT = Decimal("90.00")

    @classmethod
    @transaction.atomic
    def register_exception(  # noqa: PLR0913
        cls,
        *,
        creator_id: int,
        start_date: date,
        end_date: date,
        reason_type: str = ScheduleExceptionReason.PERSONAL,
        title: str,
        description: str = "",
        is_approved: bool = False,
        approved_by=None,
        document_url: str = "",
    ) -> ScheduleException:
        if end_date < start_date:
            msg = (
                "La fecha de fin de la excepción no puede ser anterior a la de inicio."
            )
            raise BusinessLogicError(msg)

        approved_at = timezone.now() if is_approved else None

        exc = ScheduleException.objects.create(
            creator_id=creator_id,
            start_date=start_date,
            end_date=end_date,
            reason_type=reason_type,
            title=title,
            description=description,
            is_approved=is_approved,
            approved_by=approved_by,
            approved_at=approved_at,
            document_url=document_url,
        )

        if is_approved:
            CreatorScheduleSlot.objects.filter(
                creator_id=creator_id,
                scheduled_date__gte=start_date,
                scheduled_date__lte=end_date,
                status=ScheduleSlotStatus.SCHEDULED,
            ).update(status=ScheduleSlotStatus.JUSTIFIED_ABSENCE)

        logger.info(
            "schedule_exception_registered",
            extra={"exception_id": exc.id, "creator_id": creator_id},
        )
        return exc

    @classmethod
    @transaction.atomic
    def approve_exception(
        cls,
        *,
        exception_id: int,
        approved_by,
    ) -> ScheduleException:
        exc = ScheduleException.objects.get(pk=exception_id)
        exc.is_approved = True
        exc.approved_by = approved_by
        exc.approved_at = timezone.now()
        exc.save()

        CreatorScheduleSlot.objects.filter(
            creator_id=exc.creator_id,
            scheduled_date__gte=exc.start_date,
            scheduled_date__lte=exc.end_date,
            status__in=[ScheduleSlotStatus.SCHEDULED, ScheduleSlotStatus.MISSED],
        ).update(status=ScheduleSlotStatus.JUSTIFIED_ABSENCE)

        logger.info(
            "schedule_exception_approved",
            extra={"exception_id": exception_id},
        )
        return exc

    @classmethod
    @transaction.atomic
    def calculate_monthly_compliance_summary(
        cls,
        *,
        creator_id: int,
        year: int,
        month: int,
    ) -> CreatorScheduleComplianceSummary:
        """Calcula o actualiza el consolidado de cumplimiento mensual."""
        slots = CreatorScheduleSlot.objects.filter(
            creator_id=creator_id,
            scheduled_date__year=year,
            scheduled_date__month=month,
            is_mandatory=True,
        )

        stipulated_days_count = slots.values("scheduled_date").distinct().count()
        completed_days_count = (
            slots.filter(status=ScheduleSlotStatus.COMPLETED)
            .values("scheduled_date")
            .distinct()
            .count()
        )
        late_days_count = (
            slots.filter(status=ScheduleSlotStatus.LATE)
            .values("scheduled_date")
            .distinct()
            .count()
        )
        partial_days_count = (
            slots.filter(status=ScheduleSlotStatus.PARTIAL)
            .values("scheduled_date")
            .distinct()
            .count()
        )
        missed_days_count = (
            slots.filter(status=ScheduleSlotStatus.MISSED)
            .values("scheduled_date")
            .distinct()
            .count()
        )
        justified_days_count = (
            slots.filter(status=ScheduleSlotStatus.JUSTIFIED_ABSENCE)
            .values("scheduled_date")
            .distinct()
            .count()
        )

        stipulated_hours = Decimal("0.00")
        actual_hours = Decimal("0.00")
        justified_hours = Decimal("0.00")
        on_time_starts_count = 0

        for slot in slots:
            stipulated_hours += slot.planned_hours
            actual_hours += slot.actual_hours
            if slot.status == ScheduleSlotStatus.JUSTIFIED_ABSENCE:
                justified_hours += slot.planned_hours
            elif slot.status == ScheduleSlotStatus.COMPLETED or (
                slot.status == ScheduleSlotStatus.PARTIAL
                and slot.start_delay_minutes <= cls.GRACE_PERIOD_MINUTES
            ):
                on_time_starts_count += 1

        net_required_days = stipulated_days_count - justified_days_count
        effective_fulfilled_days = completed_days_count + late_days_count
        if net_required_days > 0:
            days_rate = (
                Decimal(effective_fulfilled_days) / Decimal(net_required_days)
            ) * Decimal("100.00")
            days_compliance_rate_pct = min(
                Decimal("100.00"), days_rate.quantize(Decimal("0.01")),
            )
        else:
            days_compliance_rate_pct = (
                Decimal("100.00") if stipulated_days_count > 0 else Decimal("0.00")
            )

        net_stipulated_hours = max(Decimal("0.00"), stipulated_hours - justified_hours)
        if net_stipulated_hours > Decimal("0.00"):
            hours_rate = (actual_hours / net_stipulated_hours) * Decimal("100.00")
            hours_compliance_rate_pct = min(
                Decimal("100.00"), hours_rate.quantize(Decimal("0.01")),
            )
        else:
            hours_compliance_rate_pct = (
                Decimal("100.00")
                if stipulated_hours > Decimal("0.00")
                else Decimal("0.00")
            )

        total_executed_streams = completed_days_count + late_days_count
        if total_executed_streams > 0:
            punct_rate = (
                Decimal(on_time_starts_count) / Decimal(total_executed_streams)
            ) * Decimal("100.00")
            punctuality_rate_pct = min(
                Decimal("100.00"), punct_rate.quantize(Decimal("0.01")),
            )
        else:
            punctuality_rate_pct = Decimal("0.00")

        is_compliant = (
            hours_compliance_rate_pct >= cls.COMPLETION_THRESHOLD_PCT
            and days_compliance_rate_pct >= Decimal("85.00")
        )



        summary, _ = CreatorScheduleComplianceSummary.objects.update_or_create(
            creator_id=creator_id,
            year=year,
            month=month,
            defaults={
                "stipulated_days_count": stipulated_days_count,
                "completed_days_count": completed_days_count,
                "partial_days_count": partial_days_count,
                "late_days_count": late_days_count,
                "missed_days_count": missed_days_count,
                "justified_days_count": justified_days_count,
                "stipulated_hours": stipulated_hours,
                "justified_hours": justified_hours,
                "actual_hours": actual_hours,
                "days_compliance_rate_pct": days_compliance_rate_pct,
                "hours_compliance_rate_pct": hours_compliance_rate_pct,
                "punctuality_rate_pct": punctuality_rate_pct,
                "is_compliant": is_compliant,
            },
        )

        logger.info(
            "compliance_summary_calculated",
            extra={
                "summary_id": summary.id,
                "creator_id": creator_id,
                "year": year,
                "month": month,
                "is_compliant": is_compliant,
            },
        )
        return summary
