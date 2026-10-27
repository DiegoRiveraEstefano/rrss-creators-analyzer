from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.schedules.filters import (
    CreatorScheduleComplianceSummaryFilter,
)
from rrss_creatos_analyzer.apps.schedules.forms import ComplianceRecalculateForm
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleComplianceSummary
from rrss_creatos_analyzer.apps.schedules.selectors import ScheduleSelector
from rrss_creatos_analyzer.apps.schedules.services import ScheduleService
from rrss_creatos_analyzer.apps.schedules.tables import (
    CreatorScheduleComplianceSummaryTable,
)


class ComplianceSummaryListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = CreatorScheduleComplianceSummary
    permission_required = "schedules.view_creatorschedulecompliancesummary"
    table_class = CreatorScheduleComplianceSummaryTable
    filterset_class = CreatorScheduleComplianceSummaryFilter
    template_name = "schedules/compliance_list.html"
    paginate_by = 25
    page_title = "Auditoría de Cumplimiento Mensual"
    page_subtitle = "Cómputo de horas pactadas vs horas cumplidas y puntualidad"

    def get_queryset(self):
        return ScheduleSelector.get_visible_compliance_summaries(
            user=self.request.user,
        )


class ComplianceSummaryDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = CreatorScheduleComplianceSummary
    permission_required = "schedules.view_creatorschedulecompliancesummary"
    template_name = "schedules/compliance_detail.html"
    page_title = "Detalle de Cumplimiento Mensual"
    list_url_name = "schedules:compliance_list"

    def get_queryset(self):
        return ScheduleSelector.get_visible_compliance_summaries(
            user=self.request.user,
        )


class ComplianceRecalculateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    FormView,
):
    form_class = ComplianceRecalculateForm
    permission_required = "schedules.change_creatorschedulecompliancesummary"
    template_name = "schedules/compliance_recalculate_form.html"
    page_title = "Recalcular Cumplimiento Mensual"
    page_subtitle = "Auditar horas y días cumplidos de un creador en un mes"
    success_url = reverse_lazy("schedules:compliance_list")

    def form_valid(self, form):
        data = form.cleaned_data
        summary = ScheduleService.calculate_monthly_compliance_summary(
            creator_id=data["creator"].id,
            year=data["year"],
            month=data["month"],
        )
        msg = (
            f"Resumen {summary.month:02d}/{summary.year} recalculado exitosamente. "
            f"Cumplimiento: {summary.hours_compliance_rate_pct}%"
        )
        messages.success(self.request, msg)
        return redirect(summary.get_absolute_url())


class ScheduleCalendarView(LoginRequiredMixin, CrudContextMixin, TemplateView):
    template_name = "schedules/calendar.html"
    page_title = "Calendario de Emisiones y Cumplimiento"
    page_subtitle = "Visualización cronológica de compromisos de streaming"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        start_date = today.replace(day=1)
        end_date = (start_date + timezone.timedelta(days=35)).replace(day=1)
        context["calendar_events"] = ScheduleSelector.get_slots_for_calendar(
            user=self.request.user,
            start_date=start_date,
            end_date=end_date,
        )
        return context
