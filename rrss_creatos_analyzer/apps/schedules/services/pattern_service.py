import logging
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal

from dateutil.rrule import rrulestr
from django.db import transaction
from django.db.models import Q

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.schedules.choices import DayOfWeek
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException
from rrss_creatos_analyzer.apps.schedules.rrule_utils import build_rrule_from_components
from rrss_creatos_analyzer.apps.schedules.rrule_utils import validate_rrule

logger = logging.getLogger(__name__)

DAY_MAP_REV = {
    DayOfWeek.MONDAY: "MO",
    DayOfWeek.TUESDAY: "TU",
    DayOfWeek.WEDNESDAY: "WE",
    DayOfWeek.THURSDAY: "TH",
    DayOfWeek.FRIDAY: "FR",
    DayOfWeek.SATURDAY: "SA",
    DayOfWeek.SUNDAY: "SU",
}


class PatternService:
    """Gestión de pautas recurrentes con RRULE y generación masiva de slots."""

    @classmethod
    @transaction.atomic
    def save_schedule_pattern(  # noqa: PLR0913
        cls,
        *,
        instance: CreatorSchedulePattern | None = None,
        creator_id: int,
        rrule: str,
        title: str = "",
        start_time: time,
        end_time: time,
        planned_duration_minutes: int,
        channel_id: int | None = None,
        platform: str = "twitch",
        category_or_game: str = "Just Chatting",
        is_mandatory: bool = True,
        effective_from: date,
        effective_until: date | None = None,
        is_active: bool = True,
        notes: str = "",
    ) -> CreatorSchedulePattern:
        if planned_duration_minutes <= 0:
            msg = "La duración estipulada debe ser estrictamente mayor a 0 minutos."
            raise BusinessLogicError(msg)

        if effective_until and effective_until < effective_from:
            msg = "La fecha de fin de vigencia no puede ser anterior a la de inicio."
            raise BusinessLogicError(msg)

        try:
            validate_rrule(rrule)
        except Exception as exc:
            raise BusinessLogicError(str(exc)) from exc

        # Validación RN-SCH-002: no superposición horaria en fechas coincidentes
        if is_active:
            cls._validate_pattern_overlap(
                instance=instance,
                creator_id=creator_id,
                rrule_str=rrule,
                start_time=start_time,
                end_time=end_time,
                effective_from=effective_from,
                effective_until=effective_until,
            )

        pattern = instance or CreatorSchedulePattern()
        pattern.creator_id = creator_id
        pattern.title = title
        pattern.channel_id = channel_id
        pattern.platform = platform
        pattern.rrule = rrule
        pattern.start_time = start_time
        pattern.end_time = end_time
        pattern.planned_duration_minutes = planned_duration_minutes
        pattern.category_or_game = category_or_game
        pattern.is_mandatory = is_mandatory
        pattern.effective_from = effective_from
        pattern.effective_until = effective_until
        pattern.is_active = is_active
        pattern.notes = notes
        pattern.save()

        logger.info(
            "schedule_pattern_saved",
            extra={"pattern_id": pattern.id, "creator_id": creator_id},
        )
        return pattern

    @classmethod
    def save_weekly_schedule(  # noqa: PLR0913
        cls,
        *,
        instance: CreatorSchedulePattern | None = None,
        creator_id: int,
        day_of_week: int,
        start_time: time,
        end_time: time,
        planned_duration_minutes: int,
        channel_id: int | None = None,
        platform: str = "twitch",
        category_or_game: str = "Just Chatting",
        is_mandatory: bool = True,
        effective_from: date,
        effective_until: date | None = None,
        is_active: bool = True,
        notes: str = "",
        title: str = "",
    ) -> CreatorSchedulePattern:
        """Adaptador de compatibilidad para pautas creadas por día de la semana."""
        day_code = DAY_MAP_REV.get(day_of_week, "MO")
        rrule_str = build_rrule_from_components(
            freq="WEEKLY",
            interval=1,
            byday=[day_code],
        )
        return cls.save_schedule_pattern(
            instance=instance,
            creator_id=creator_id,
            rrule=rrule_str,
            title=title,
            start_time=start_time,
            end_time=end_time,
            planned_duration_minutes=planned_duration_minutes,
            channel_id=channel_id,
            platform=platform,
            category_or_game=category_or_game,
            is_mandatory=is_mandatory,
            effective_from=effective_from,
            effective_until=effective_until,
            is_active=is_active,
            notes=notes,
        )

    @classmethod
    def _validate_pattern_overlap(  # noqa: PLR0913
        cls,
        *,
        instance: CreatorSchedulePattern | None,
        creator_id: int,
        rrule_str: str,
        start_time: time,
        end_time: time,
        effective_from: date,
        effective_until: date | None,
    ) -> None:
        """Verifica que no existan colisiones de slots en horizonte de 90 días."""
        other_patterns = CreatorSchedulePattern.objects.filter(
            creator_id=creator_id,
            is_active=True,
        )
        if instance and instance.pk:
            other_patterns = other_patterns.exclude(pk=instance.pk)

        if not other_patterns.exists():
            return

        horizon_end = effective_from + timedelta(days=90)
        if effective_until and effective_until < horizon_end:
            horizon_end = effective_until

        test_dtstart = datetime.combine(effective_from, start_time)
        try:
            current_rule = rrulestr(rrule_str, dtstart=test_dtstart)
            current_occurrences = {
                dt.date()
                for dt in current_rule.between(
                    datetime.combine(effective_from, time.min),
                    datetime.combine(horizon_end, time.max),
                    inc=True,
                )
            }
        except Exception:  # noqa: BLE001
            return

        if not current_occurrences:
            return

        for other in other_patterns:
            times_overlap = (
                other.start_time <= start_time < other.end_time
                or other.start_time < end_time <= other.end_time
                or (start_time <= other.start_time and end_time >= other.end_time)
            )
            if not times_overlap:
                continue

            other_dtstart = datetime.combine(other.effective_from, other.start_time)
            try:
                other_rule = rrulestr(other.rrule, dtstart=other_dtstart)
                other_end = (
                    min(horizon_end, other.effective_until)
                    if other.effective_until
                    else horizon_end
                )
                other_dates = {
                    dt.date()
                    for dt in other_rule.between(
                        datetime.combine(other.effective_from, time.min),
                        datetime.combine(other_end, time.max),
                        inc=True,
                    )
                }
            except Exception:  # noqa: BLE001, S112
                continue

            shared_dates = current_occurrences.intersection(other_dates)
            if shared_dates:
                first_date = sorted(shared_dates)[0]
                msg = (
                    f"Existe superposición horaria con la pauta '{other}' "
                    f"en la fecha {first_date.strftime('%d/%m/%Y')}."
                )
                raise BusinessLogicError(msg)

    @classmethod
    @transaction.atomic
    def generate_slots_for_period(
        cls,
        *,
        start_date: date,
        end_date: date,
        creator_id: int | None = None,
    ) -> int:
        """Genera slots concretos a partir de pautas RRULE de forma idempotente."""
        if end_date < start_date:
            msg = "La fecha de fin debe ser posterior o igual a la de inicio."
            raise BusinessLogicError(msg)

        patterns_qs = CreatorSchedulePattern.objects.filter(
            is_active=True,
            effective_from__lte=end_date,
        ).filter(Q(effective_until__isnull=True) | Q(effective_until__gte=start_date))

        if creator_id:
            patterns_qs = patterns_qs.filter(creator_id=creator_id)

        created_count = 0
        patterns_list = list(patterns_qs.select_related("creator", "channel"))

        for pattern in patterns_list:
            dtstart = datetime.combine(pattern.effective_from, pattern.start_time)
            try:
                rule = rrulestr(pattern.rrule, dtstart=dtstart)
            except Exception:
                logger.exception(
                    "invalid_rrule_in_pattern",
                    extra={"pattern_id": pattern.id},
                )
                continue

            win_start_date = max(start_date, pattern.effective_from)
            win_end_date = (
                min(end_date, pattern.effective_until)
                if pattern.effective_until
                else end_date
            )
            if win_end_date < win_start_date:
                continue

            occurrences = rule.between(
                datetime.combine(win_start_date, time.min),
                datetime.combine(win_end_date, time.max),
                inc=True,
            )

            for occ_dt in occurrences:
                slot_date = occ_dt.date()
                exists = CreatorScheduleSlot.objects.filter(
                    creator_id=pattern.creator_id,
                    scheduled_date=slot_date,
                    scheduled_start_time=pattern.start_time,
                ).exists()

                if exists:
                    continue

                has_exception = ScheduleException.objects.filter(
                    creator_id=pattern.creator_id,
                    is_approved=True,
                    start_date__lte=slot_date,
                    end_date__gte=slot_date,
                ).exists()

                initial_status = (
                    ScheduleSlotStatus.JUSTIFIED_ABSENCE
                    if has_exception
                    else ScheduleSlotStatus.SCHEDULED
                )

                planned_hours = (
                    Decimal(pattern.planned_duration_minutes) / Decimal(60)
                ).quantize(Decimal("0.01"))

                label = pattern.title or pattern.human_recurrence
                slot_title = f"{pattern.creator.display_name} - {label}"

                CreatorScheduleSlot.objects.create(
                    creator_id=pattern.creator_id,
                    channel_id=pattern.channel_id,
                    schedule_pattern=pattern,
                    scheduled_date=slot_date,
                    scheduled_start_time=pattern.start_time,
                    scheduled_end_time=pattern.end_time,
                    planned_duration_minutes=pattern.planned_duration_minutes,
                    planned_hours=planned_hours,
                    title=slot_title,
                    category_or_game=pattern.category_or_game,
                    status=initial_status,
                    is_mandatory=pattern.is_mandatory,
                )
                created_count += 1

        logger.info(
            "slots_generated_for_period",
            extra={
                "start_date": str(start_date),
                "end_date": str(end_date),
                "created_count": created_count,
            },
        )
        return created_count
