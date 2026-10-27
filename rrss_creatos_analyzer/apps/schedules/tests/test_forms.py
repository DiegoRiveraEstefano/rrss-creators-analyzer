import pytest

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.forms import ComplianceRecalculateForm
from rrss_creatos_analyzer.apps.schedules.forms import CreatorSchedulePatternForm
from rrss_creatos_analyzer.apps.schedules.forms import CreatorScheduleSlotForm
from rrss_creatos_analyzer.apps.schedules.forms import GenerateSlotsForm
from rrss_creatos_analyzer.apps.schedules.forms import ScheduleExceptionForm

pytestmark = pytest.mark.django_db


class TestScheduleForms:
    def test_schedule_pattern_form_with_direct_rrule(self):
        creator = CreatorFactory()
        form = CreatorSchedulePatternForm(
            data={
                "creator": creator.pk,
                "title": "Streams Nocturnos",
                "platform": PlatformType.TWITCH,
                "rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1",
                "start_time": "18:00",
                "end_time": "22:00",
                "planned_duration_minutes": 240,
                "category_or_game": "Just Chatting",
                "is_mandatory": True,
                "effective_from": "2026-10-01",
                "is_active": True,
            },
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["rrule"] == "FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1"

    def test_schedule_pattern_form_with_builder_fields(self):
        creator = CreatorFactory()
        form = CreatorSchedulePatternForm(
            data={
                "creator": creator.pk,
                "title": "Streams Fin de Semana",
                "platform": PlatformType.TWITCH,
                "recurrence_freq": "WEEKLY",
                "recurrence_interval": 2,
                "recurrence_days": ["SA", "SU"],
                "start_time": "16:00",
                "end_time": "20:00",
                "planned_duration_minutes": 240,
                "category_or_game": "Gaming",
                "is_mandatory": True,
                "effective_from": "2026-10-01",
                "is_active": True,
            },
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["rrule"] == "FREQ=WEEKLY;INTERVAL=2;BYDAY=SA,SU"

    def test_schedule_pattern_form_invalid_rrule(self):
        creator = CreatorFactory()
        form = CreatorSchedulePatternForm(
            data={
                "creator": creator.pk,
                "rrule": "INVALID_RRULE_FORMAT",
                "start_time": "18:00",
                "end_time": "22:00",
                "planned_duration_minutes": 240,
                "effective_from": "2026-10-01",
            },
        )
        assert not form.is_valid()
        assert "rrule" in form.errors

    def test_slot_form_valid(self):
        creator = CreatorFactory()
        form = CreatorScheduleSlotForm(
            data={
                "creator": creator.pk,
                "scheduled_date": "2026-10-28",
                "scheduled_start_time": "19:00",
                "scheduled_end_time": "23:00",
                "planned_duration_minutes": 240,
                "planned_hours": "4.00",
                "title": "Stream Especial",
                "category_or_game": "Valorant",
                "status": ScheduleSlotStatus.SCHEDULED,
                "is_mandatory": True,
            },
        )
        assert form.is_valid(), form.errors

    def test_generate_slots_form_valid(self):
        form = GenerateSlotsForm(
            data={
                "start_date": "2026-11-01",
                "end_date": "2026-11-30",
            },
        )
        assert form.is_valid(), form.errors

    def test_schedule_exception_form_valid(self):
        creator = CreatorFactory()
        form = ScheduleExceptionForm(
            data={
                "creator": creator.pk,
                "reason_type": ScheduleExceptionReason.VACATION,
                "title": "Vacaciones Anuales",
                "start_date": "2026-12-15",
                "end_date": "2026-12-30",
            },
        )
        assert form.is_valid(), form.errors

    def test_compliance_recalculate_form_valid(self):
        creator = CreatorFactory()
        form = ComplianceRecalculateForm(
            data={
                "creator": creator.pk,
                "year": 2026,
                "month": 10,
            },
        )
        assert form.is_valid(), form.errors
