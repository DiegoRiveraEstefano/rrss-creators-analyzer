from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Sum

from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException

if TYPE_CHECKING:
    from datetime import date

    from django.contrib.auth.models import AbstractBaseUser


class ScheduleSelector:
    """Consultas optimizadas y puras de solo lectura para el dominio de Schedules."""

    @classmethod
    def _is_agency_staff(cls, user: AbstractBaseUser) -> bool:
        if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
            return True
        return user.has_perm("schedules.view_creatorschedulepattern") or user.has_perm(
            "creators.view_all_creators",
        )

    @classmethod
    def get_visible_schedule_patterns(cls, *, user) -> QuerySet[CreatorSchedulePattern]:
        qs = CreatorSchedulePattern.objects.select_related("creator", "channel")
        if cls._is_agency_staff(user):
            return qs
        return qs.filter(creator__user=user)

    # Alias para compatibilidad retroactiva
    get_visible_weekly_schedules = get_visible_schedule_patterns

    @classmethod
    def get_visible_slots(cls, *, user) -> QuerySet[CreatorScheduleSlot]:
        qs = CreatorScheduleSlot.objects.select_related(
            "creator",
            "channel",
            "schedule_pattern",
            "actual_streaming_session",
        )
        if cls._is_agency_staff(user):
            return qs
        return qs.filter(creator__user=user)

    @classmethod
    def get_visible_exceptions(cls, *, user) -> QuerySet[ScheduleException]:
        qs = ScheduleException.objects.select_related("creator", "approved_by")
        if cls._is_agency_staff(user):
            return qs
        return qs.filter(creator__user=user)

    @classmethod
    def get_visible_compliance_summaries(
        cls,
        *,
        user,
    ) -> QuerySet[CreatorScheduleComplianceSummary]:
        qs = CreatorScheduleComplianceSummary.objects.select_related("creator")
        if cls._is_agency_staff(user):
            return qs
        return qs.filter(creator__user=user)

    @classmethod
    def get_slots_for_calendar(
        cls,
        *,
        user,
        start_date: date,
        end_date: date,
        creator_id: int | None = None,
    ) -> list[dict[str, Any]]:
        qs = cls.get_visible_slots(user=user).filter(
            scheduled_date__gte=start_date,
            scheduled_date__lte=end_date,
        )
        if creator_id:
            qs = qs.filter(creator_id=creator_id)

        return [
            {
                "id": slot.id,
                "title": f"{slot.creator.display_name}: {slot.title}",
                "start": f"{slot.scheduled_date}T{slot.scheduled_start_time}",
                "end": f"{slot.scheduled_date}T{slot.scheduled_end_time}",
                "status": slot.status,
                "status_display": slot.get_status_display(),
                "planned_hours": float(slot.planned_hours),
                "actual_hours": float(slot.actual_hours),
                "url": slot.get_absolute_url(),
            }
            for slot in qs
        ]

    @classmethod
    def get_creator_monthly_stats(
        cls,
        *,
        creator_id: int,
        year: int,
        month: int,
    ) -> dict[str, Any]:
        slots = CreatorScheduleSlot.objects.filter(
            creator_id=creator_id,
            scheduled_date__year=year,
            scheduled_date__month=month,
        )
        return slots.aggregate(
            total_slots=Count("id"),
            completed_slots=Count(
                "id",
                filter=Q(
                    status__in=[
                        ScheduleSlotStatus.COMPLETED,
                        ScheduleSlotStatus.LATE,
                    ],
                ),
            ),
            missed_slots=Count(
                "id",
                filter=Q(status=ScheduleSlotStatus.MISSED),
            ),
            justified_slots=Count(
                "id",
                filter=Q(status=ScheduleSlotStatus.JUSTIFIED_ABSENCE),
            ),
            planned_hours=Sum("planned_hours"),
            actual_hours=Sum("actual_hours"),
            avg_compliance_rate=Avg("compliance_rate_pct"),
        )
