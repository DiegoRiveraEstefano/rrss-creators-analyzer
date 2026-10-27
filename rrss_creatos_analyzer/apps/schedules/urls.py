from django.urls import path

from rrss_creatos_analyzer.apps.schedules.views import ComplianceRecalculateView
from rrss_creatos_analyzer.apps.schedules.views import ComplianceSummaryDetailView
from rrss_creatos_analyzer.apps.schedules.views import ComplianceSummaryListView
from rrss_creatos_analyzer.apps.schedules.views import GenerateSlotsView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleCalendarView
from rrss_creatos_analyzer.apps.schedules.views import (
    ScheduleExceptionApproveActionView,
)
from rrss_creatos_analyzer.apps.schedules.views import ScheduleExceptionCreateView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleExceptionDeleteView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleExceptionDetailView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleExceptionListView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleExceptionUpdateView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleSlotCreateView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleSlotDeleteView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleSlotDetailView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleSlotListView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleSlotReconcileActionView
from rrss_creatos_analyzer.apps.schedules.views import ScheduleSlotUpdateView
from rrss_creatos_analyzer.apps.schedules.views import WeeklyScheduleCreateView
from rrss_creatos_analyzer.apps.schedules.views import WeeklyScheduleDeleteView
from rrss_creatos_analyzer.apps.schedules.views import WeeklyScheduleDetailView
from rrss_creatos_analyzer.apps.schedules.views import WeeklyScheduleListView
from rrss_creatos_analyzer.apps.schedules.views import WeeklyScheduleUpdateView

app_name = "schedules"

urlpatterns = [
    # Calendario y Vista General
    path("", ScheduleCalendarView.as_view(), name="calendar"),
    # Pautas Recurrentes (RRULE)
    path("patterns/", WeeklyScheduleListView.as_view(), name="pattern_list"),
    path(
        "patterns/create/",
        WeeklyScheduleCreateView.as_view(),
        name="pattern_create",
    ),
    path(
        "patterns/<int:pk>/",
        WeeklyScheduleDetailView.as_view(),
        name="pattern_detail",
    ),
    path(
        "patterns/<int:pk>/update/",
        WeeklyScheduleUpdateView.as_view(),
        name="pattern_update",
    ),
    path(
        "patterns/<int:pk>/delete/",
        WeeklyScheduleDeleteView.as_view(),
        name="pattern_delete",
    ),
    # Pautas Semanales (Compatibilidad retroactiva)
    path("weekly/", WeeklyScheduleListView.as_view(), name="weekly_list"),
    path(
        "weekly/create/",
        WeeklyScheduleCreateView.as_view(),
        name="weekly_create",
    ),
    path(
        "weekly/<int:pk>/",
        WeeklyScheduleDetailView.as_view(),
        name="weekly_detail",
    ),
    path(
        "weekly/<int:pk>/update/",
        WeeklyScheduleUpdateView.as_view(),
        name="weekly_update",
    ),
    path(
        "weekly/<int:pk>/delete/",
        WeeklyScheduleDeleteView.as_view(),
        name="weekly_delete",
    ),
    # Slots de Transmisión
    path("slots/", ScheduleSlotListView.as_view(), name="slot_list"),
    path("slots/create/", ScheduleSlotCreateView.as_view(), name="slot_create"),
    path("slots/generate/", GenerateSlotsView.as_view(), name="slot_generate"),
    path("slots/<int:pk>/", ScheduleSlotDetailView.as_view(), name="slot_detail"),
    path(
        "slots/<int:pk>/update/",
        ScheduleSlotUpdateView.as_view(),
        name="slot_update",
    ),
    path(
        "slots/<int:pk>/delete/",
        ScheduleSlotDeleteView.as_view(),
        name="slot_delete",
    ),
    path(
        "slots/<int:pk>/reconcile/",
        ScheduleSlotReconcileActionView.as_view(),
        name="slot_reconcile",
    ),
    # Excepciones y Permisos
    path("exceptions/", ScheduleExceptionListView.as_view(), name="exception_list"),
    path(
        "exceptions/create/",
        ScheduleExceptionCreateView.as_view(),
        name="exception_create",
    ),
    path(
        "exceptions/<int:pk>/",
        ScheduleExceptionDetailView.as_view(),
        name="exception_detail",
    ),
    path(
        "exceptions/<int:pk>/update/",
        ScheduleExceptionUpdateView.as_view(),
        name="exception_update",
    ),
    path(
        "exceptions/<int:pk>/delete/",
        ScheduleExceptionDeleteView.as_view(),
        name="exception_delete",
    ),
    path(
        "exceptions/<int:pk>/approve/",
        ScheduleExceptionApproveActionView.as_view(),
        name="exception_approve",
    ),
    # Auditoría y Cumplimiento Mensual
    path("compliance/", ComplianceSummaryListView.as_view(), name="compliance_list"),
    path(
        "compliance/recalculate/",
        ComplianceRecalculateView.as_view(),
        name="compliance_recalculate",
    ),
    path(
        "compliance/<int:pk>/",
        ComplianceSummaryDetailView.as_view(),
        name="compliance_detail",
    ),
]
