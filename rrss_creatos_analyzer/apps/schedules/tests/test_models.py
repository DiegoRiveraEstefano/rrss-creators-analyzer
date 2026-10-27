from datetime import date
from datetime import time
from decimal import Decimal

import pytest
from django.db import IntegrityError

from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorScheduleComplianceSummaryFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorSchedulePatternFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorScheduleSlotFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    ScheduleExceptionFactory,
)

pytestmark = pytest.mark.django_db


class TestCreatorSchedulePatternModel:
    def test_str_representation(self):
        pattern = CreatorSchedulePatternFactory(
            title="",
            rrule="FREQ=WEEKLY;BYDAY=MO;INTERVAL=1",
            start_time=time(18, 0),
            end_time=time(22, 0),
        )
        assert pattern.creator.display_name in str(pattern)
        assert "Lunes" in str(pattern)
        assert pattern.get_absolute_url() == f"/schedules/patterns/{pattern.pk}/"

    def test_planned_duration_must_be_positive(self):
        with pytest.raises(IntegrityError):
            CreatorSchedulePatternFactory(planned_duration_minutes=0)

    def test_effective_dates_coherence(self):
        with pytest.raises(IntegrityError):
            CreatorSchedulePatternFactory(
                effective_from=date(2026, 5, 10),
                effective_until=date(2026, 5, 1),
            )


class TestCreatorScheduleSlotModel:
    def test_str_representation(self):
        slot = CreatorScheduleSlotFactory(
            scheduled_date=date(2026, 10, 26),
            scheduled_start_time=time(18, 0),
            status=ScheduleSlotStatus.SCHEDULED,
        )
        assert slot.creator.display_name in str(slot)
        assert "26/10/2026" in str(slot)
        assert slot.get_absolute_url() == f"/schedules/slots/{slot.pk}/"

    def test_unique_creator_date_start_time(self):
        slot1 = CreatorScheduleSlotFactory(
            scheduled_date=date(2026, 10, 28),
            scheduled_start_time=time(18, 0),
        )
        with pytest.raises(IntegrityError):
            CreatorScheduleSlotFactory(
                creator=slot1.creator,
                scheduled_date=date(2026, 10, 28),
                scheduled_start_time=time(18, 0),
            )

    def test_positive_hours_constraint(self):
        with pytest.raises(IntegrityError):
            CreatorScheduleSlotFactory(planned_hours=Decimal("-1.00"))


class TestScheduleExceptionModel:
    def test_str_representation(self):
        exc = ScheduleExceptionFactory(
            title="Licencia Médica",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 5),
        )
        assert exc.creator.display_name in str(exc)
        assert "Licencia Médica" in str(exc)
        assert exc.get_absolute_url() == f"/schedules/exceptions/{exc.pk}/"

    def test_dates_coherence_constraint(self):
        with pytest.raises(IntegrityError):
            ScheduleExceptionFactory(
                start_date=date(2026, 10, 10),
                end_date=date(2026, 10, 5),
            )


class TestCreatorScheduleComplianceSummaryModel:
    def test_str_representation(self):
        summary = CreatorScheduleComplianceSummaryFactory(
            year=2026,
            month=10,
        )
        assert summary.creator.display_name in str(summary)
        assert "10/2026" in str(summary)
        assert summary.get_absolute_url() == f"/schedules/compliance/{summary.pk}/"

    def test_unique_creator_year_month(self):
        s1 = CreatorScheduleComplianceSummaryFactory(year=2026, month=10)
        with pytest.raises(IntegrityError):
            CreatorScheduleComplianceSummaryFactory(
                creator=s1.creator,
                year=2026,
                month=10,
            )
