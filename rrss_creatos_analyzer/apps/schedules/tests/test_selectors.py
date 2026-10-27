from datetime import date
from decimal import Decimal

import pytest

from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.selectors import ScheduleSelector
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorScheduleSlotFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorWeeklyScheduleFactory,
)
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestScheduleSelector:
    def test_visible_weekly_schedules_staff_vs_creator(self):
        admin = UserFactory(is_staff=True, is_superuser=True)
        creator_user = UserFactory(is_staff=False, is_superuser=False)
        creator = CreatorFactory(user=creator_user)
        other_creator = CreatorFactory()

        sched1 = CreatorWeeklyScheduleFactory(creator=creator)
        CreatorWeeklyScheduleFactory(creator=other_creator)

        # Admin ve ambos
        admin_qs = ScheduleSelector.get_visible_weekly_schedules(user=admin)
        assert admin_qs.count() == 2  # noqa: PLR2004

        # Creador ve solo el suyo
        creator_qs = ScheduleSelector.get_visible_weekly_schedules(user=creator_user)
        assert creator_qs.count() == 1
        assert creator_qs.first() == sched1

    def test_visible_slots_staff_vs_creator(self):
        manager = UserFactory(is_staff=True)
        creator_user = UserFactory(is_staff=False, is_superuser=False)
        creator = CreatorFactory(user=creator_user)
        other_creator = CreatorFactory()

        slot1 = CreatorScheduleSlotFactory(creator=creator)
        CreatorScheduleSlotFactory(creator=other_creator)

        manager_qs = ScheduleSelector.get_visible_slots(user=manager)
        assert manager_qs.count() == 2  # noqa: PLR2004

        creator_qs = ScheduleSelector.get_visible_slots(user=creator_user)
        assert creator_qs.count() == 1
        assert creator_qs.first() == slot1

    def test_get_slots_for_calendar(self):
        admin = UserFactory(is_staff=True, is_superuser=True)
        creator = CreatorFactory()
        CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 15),
            planned_hours=Decimal("3.00"),
        )
        events = ScheduleSelector.get_slots_for_calendar(
            user=admin,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 31),
            creator_id=creator.id,
        )
        assert len(events) == 1
        assert events[0]["planned_hours"] == 3.0  # noqa: PLR2004

    def test_get_creator_monthly_stats(self):
        creator = CreatorFactory()
        CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 5),
            status=ScheduleSlotStatus.COMPLETED,
            planned_hours=Decimal("4.00"),
            actual_hours=Decimal("4.00"),
        )
        CreatorScheduleSlotFactory(
            creator=creator,
            scheduled_date=date(2026, 10, 12),
            status=ScheduleSlotStatus.MISSED,
            planned_hours=Decimal("4.00"),
            actual_hours=Decimal("0.00"),
        )
        stats = ScheduleSelector.get_creator_monthly_stats(
            creator_id=creator.id,
            year=2026,
            month=10,
        )
        assert stats["total_slots"] == 2  # noqa: PLR2004
        assert stats["completed_slots"] == 1
        assert stats["missed_slots"] == 1
