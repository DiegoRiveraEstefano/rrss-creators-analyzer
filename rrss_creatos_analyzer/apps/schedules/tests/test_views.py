from datetime import date
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from rrss_creatos_analyzer.apps.creators.tests.factories import CreatorFactory
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorScheduleComplianceSummaryFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorScheduleSlotFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    CreatorWeeklyScheduleFactory,
)
from rrss_creatos_analyzer.apps.schedules.tests.factories import (
    ScheduleExceptionFactory,
)
from rrss_creatos_analyzer.apps.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client: Client):
    admin = UserFactory(is_staff=True, is_superuser=True)
    client.force_login(admin)
    return client


class TestScheduleViews:
    def test_calendar_view(self, admin_client: Client):
        url = reverse("schedules:calendar")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert "calendar_events" in response.context

    def test_weekly_schedule_list_and_detail(self, admin_client: Client):
        weekly = CreatorWeeklyScheduleFactory()
        list_url = reverse("schedules:weekly_list")
        res_list = admin_client.get(list_url)
        assert res_list.status_code == HTTPStatus.OK

        detail_url = reverse("schedules:weekly_detail", kwargs={"pk": weekly.pk})
        res_detail = admin_client.get(detail_url)
        assert res_detail.status_code == HTTPStatus.OK
        assert weekly.creator.display_name in res_detail.content.decode()

    def test_slot_list_and_detail(self, admin_client: Client):
        slot = CreatorScheduleSlotFactory()
        list_url = reverse("schedules:slot_list")
        res_list = admin_client.get(list_url)
        assert res_list.status_code == HTTPStatus.OK

        detail_url = reverse("schedules:slot_detail", kwargs={"pk": slot.pk})
        res_detail = admin_client.get(detail_url)
        assert res_detail.status_code == HTTPStatus.OK

    def test_generate_slots_view(self, admin_client: Client):
        creator = CreatorFactory()
        CreatorWeeklyScheduleFactory(
            creator=creator,
            rrule="FREQ=WEEKLY;BYDAY=FR;INTERVAL=1",
            effective_from=date(2026, 10, 1),
        )
        url = reverse("schedules:slot_generate")
        res_get = admin_client.get(url)
        assert res_get.status_code == HTTPStatus.OK

        res_post = admin_client.post(
            url,
            data={
                "creator": creator.pk,
                "start_date": "2026-10-01",
                "end_date": "2026-10-10",
            },
            follow=True,
        )
        assert res_post.status_code == HTTPStatus.OK
        assert CreatorScheduleSlot.objects.filter(creator=creator).exists()

    def test_slot_reconcile_action_view(self, admin_client: Client):
        slot = CreatorScheduleSlotFactory(
            scheduled_date=date(2026, 10, 1),
        )
        url = reverse("schedules:slot_reconcile", kwargs={"pk": slot.pk})
        response = admin_client.post(url, follow=True)
        assert response.status_code == HTTPStatus.OK
        slot.refresh_from_db()
        assert slot.status == ScheduleSlotStatus.MISSED

    def test_exception_list_and_approve_action(self, admin_client: Client):
        exc = ScheduleExceptionFactory(is_approved=False)
        list_url = reverse("schedules:exception_list")
        assert admin_client.get(list_url).status_code == HTTPStatus.OK

        approve_url = reverse("schedules:exception_approve", kwargs={"pk": exc.pk})
        res_approve = admin_client.post(approve_url, follow=True)
        assert res_approve.status_code == HTTPStatus.OK
        exc.refresh_from_db()
        assert exc.is_approved is True

    def test_compliance_summary_views(self, admin_client: Client):
        summary = CreatorScheduleComplianceSummaryFactory()
        list_url = reverse("schedules:compliance_list")
        assert admin_client.get(list_url).status_code == HTTPStatus.OK

        detail_url = reverse("schedules:compliance_detail", kwargs={"pk": summary.pk})
        assert admin_client.get(detail_url).status_code == HTTPStatus.OK
