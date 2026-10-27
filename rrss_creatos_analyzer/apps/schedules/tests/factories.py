from __future__ import annotations

from datetime import date
from datetime import time
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException


class CreatorSchedulePatternFactory(DjangoModelFactory[CreatorSchedulePattern]):
    creator = factory.SubFactory(CreatorFactory)
    title = "Streams Nocturnos"
    platform = PlatformType.TWITCH
    rrule = "FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1"
    start_time = time(18, 0)
    end_time = time(22, 0)
    planned_duration_minutes = 240
    category_or_game = "Just Chatting"
    is_mandatory = True
    effective_from = date(2026, 1, 1)
    is_active = True

    class Meta:
        model = CreatorSchedulePattern


CreatorWeeklyScheduleFactory = CreatorSchedulePatternFactory


class CreatorScheduleSlotFactory(DjangoModelFactory[CreatorScheduleSlot]):
    creator = factory.SubFactory(CreatorFactory)
    scheduled_date = date(2026, 10, 26)
    scheduled_start_time = time(18, 0)
    scheduled_end_time = time(22, 0)
    planned_duration_minutes = 240
    planned_hours = Decimal("4.00")
    title = "Directo Nocturno"
    category_or_game = "Just Chatting"
    status = ScheduleSlotStatus.SCHEDULED
    is_mandatory = True

    class Meta:
        model = CreatorScheduleSlot


class ScheduleExceptionFactory(DjangoModelFactory[ScheduleException]):
    creator = factory.SubFactory(CreatorFactory)
    start_date = date(2026, 10, 20)
    end_date = date(2026, 10, 22)
    reason_type = ScheduleExceptionReason.MEDICAL
    title = "Reposo Médico"
    description = "Licencia por faringitis"
    is_approved = True

    class Meta:
        model = ScheduleException


class CreatorScheduleComplianceSummaryFactory(
    DjangoModelFactory[CreatorScheduleComplianceSummary],
):
    creator = factory.SubFactory(CreatorFactory)
    year = 2026
    month = 10
    stipulated_days_count = 15
    completed_days_count = 14
    late_days_count = 1
    justified_days_count = 0
    missed_days_count = 0
    stipulated_hours = Decimal("60.00")
    actual_hours = Decimal("58.50")
    justified_hours = Decimal("0.00")
    days_compliance_rate_pct = Decimal("100.00")
    hours_compliance_rate_pct = Decimal("97.50")
    punctuality_rate_pct = Decimal("93.33")
    is_compliant = True

    class Meta:
        model = CreatorScheduleComplianceSummary
