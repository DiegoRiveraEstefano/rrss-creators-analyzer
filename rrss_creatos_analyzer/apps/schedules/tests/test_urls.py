from django.urls import resolve
from django.urls import reverse


def test_calendar_url():
    assert reverse("schedules:calendar") == "/schedules/"
    assert resolve("/schedules/").view_name == "schedules:calendar"


def test_weekly_urls():
    assert reverse("schedules:weekly_list") == "/schedules/weekly/"
    assert reverse("schedules:weekly_create") == "/schedules/weekly/create/"
    assert (
        reverse("schedules:weekly_detail", kwargs={"pk": 1}) == "/schedules/weekly/1/"
    )
    assert (
        reverse("schedules:weekly_update", kwargs={"pk": 1})
        == "/schedules/weekly/1/update/"
    )
    assert (
        reverse("schedules:weekly_delete", kwargs={"pk": 1})
        == "/schedules/weekly/1/delete/"
    )


def test_slot_urls():
    assert reverse("schedules:slot_list") == "/schedules/slots/"
    assert reverse("schedules:slot_create") == "/schedules/slots/create/"
    assert reverse("schedules:slot_generate") == "/schedules/slots/generate/"
    assert reverse("schedules:slot_detail", kwargs={"pk": 1}) == "/schedules/slots/1/"
    assert (
        reverse("schedules:slot_update", kwargs={"pk": 1})
        == "/schedules/slots/1/update/"
    )
    assert (
        reverse("schedules:slot_delete", kwargs={"pk": 1})
        == "/schedules/slots/1/delete/"
    )
    assert (
        reverse("schedules:slot_reconcile", kwargs={"pk": 1})
        == "/schedules/slots/1/reconcile/"
    )


def test_exception_urls():
    assert reverse("schedules:exception_list") == "/schedules/exceptions/"
    assert reverse("schedules:exception_create") == "/schedules/exceptions/create/"
    assert (
        reverse("schedules:exception_detail", kwargs={"pk": 1})
        == "/schedules/exceptions/1/"
    )
    assert (
        reverse("schedules:exception_update", kwargs={"pk": 1})
        == "/schedules/exceptions/1/update/"
    )
    assert (
        reverse("schedules:exception_delete", kwargs={"pk": 1})
        == "/schedules/exceptions/1/delete/"
    )
    assert (
        reverse("schedules:exception_approve", kwargs={"pk": 1})
        == "/schedules/exceptions/1/approve/"
    )


def test_compliance_urls():
    assert reverse("schedules:compliance_list") == "/schedules/compliance/"
    assert (
        reverse("schedules:compliance_recalculate")
        == "/schedules/compliance/recalculate/"
    )
    assert (
        reverse("schedules:compliance_detail", kwargs={"pk": 1})
        == "/schedules/compliance/1/"
    )
