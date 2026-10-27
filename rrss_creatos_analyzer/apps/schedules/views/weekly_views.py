from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.schedules.filters import CreatorSchedulePatternFilter
from rrss_creatos_analyzer.apps.schedules.forms import CreatorSchedulePatternForm
from rrss_creatos_analyzer.apps.schedules.models import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.schedules.selectors import ScheduleSelector
from rrss_creatos_analyzer.apps.schedules.services import ScheduleService
from rrss_creatos_analyzer.apps.schedules.tables import CreatorSchedulePatternTable


class WeeklyScheduleListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = CreatorSchedulePattern
    permission_required = "schedules.view_creatorschedulepattern"
    table_class = CreatorSchedulePatternTable
    filterset_class = CreatorSchedulePatternFilter
    template_name = "schedules/weekly_schedule_list.html"
    paginate_by = 25
    page_title = "Pautas Recurrentes de Creadores"
    page_subtitle = "Configuración de horarios recurrentes y compromisos con RRULE"
    create_url_name = "schedules:weekly_create"

    def get_queryset(self):
        return ScheduleSelector.get_visible_schedule_patterns(user=self.request.user)


class WeeklyScheduleDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = CreatorSchedulePattern
    permission_required = "schedules.view_creatorschedulepattern"
    template_name = "schedules/weekly_schedule_detail.html"
    page_title = "Detalle de Pauta Recurrente"
    list_url_name = "schedules:weekly_list"
    update_url_name = "schedules:weekly_update"
    delete_url_name = "schedules:weekly_delete"

    def get_queryset(self):
        return ScheduleSelector.get_visible_schedule_patterns(user=self.request.user)


class WeeklyScheduleCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = CreatorSchedulePattern
    form_class = CreatorSchedulePatternForm
    permission_required = "schedules.add_creatorschedulepattern"
    template_name = "schedules/weekly_schedule_form.html"
    page_title = "Nueva Pauta Recurrente"
    list_url_name = "schedules:weekly_list"

    def form_valid(self, form):
        try:
            data = form.cleaned_data
            self.object = ScheduleService.save_schedule_pattern(
                creator_id=data["creator"].id,
                channel_id=data["channel"].id if data.get("channel") else None,
                platform=data["platform"],
                rrule=data["rrule"],
                title=data.get("title", ""),
                start_time=data["start_time"],
                end_time=data["end_time"],
                planned_duration_minutes=data["planned_duration_minutes"],
                category_or_game=data["category_or_game"],
                is_mandatory=data["is_mandatory"],
                effective_from=data["effective_from"],
                effective_until=data.get("effective_until"),
                is_active=data["is_active"],
                notes=data.get("notes", ""),
            )
            messages.success(self.request, "Pauta recurrente creada exitosamente.")
            return redirect(self.object.get_absolute_url())
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class WeeklyScheduleUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = CreatorSchedulePattern
    form_class = CreatorSchedulePatternForm
    permission_required = "schedules.change_creatorschedulepattern"
    template_name = "schedules/weekly_schedule_form.html"
    page_title = "Editar Pauta Recurrente"
    list_url_name = "schedules:weekly_list"

    def get_queryset(self):
        return ScheduleSelector.get_visible_schedule_patterns(user=self.request.user)

    def form_valid(self, form):
        try:
            data = form.cleaned_data
            self.object = ScheduleService.save_schedule_pattern(
                instance=self.get_object(),
                creator_id=data["creator"].id,
                channel_id=data["channel"].id if data.get("channel") else None,
                platform=data["platform"],
                rrule=data["rrule"],
                title=data.get("title", ""),
                start_time=data["start_time"],
                end_time=data["end_time"],
                planned_duration_minutes=data["planned_duration_minutes"],
                category_or_game=data["category_or_game"],
                is_mandatory=data["is_mandatory"],
                effective_from=data["effective_from"],
                effective_until=data.get("effective_until"),
                is_active=data["is_active"],
                notes=data.get("notes", ""),
            )
            messages.success(
                self.request,
                "Pauta recurrente actualizada exitosamente.",
            )
            return redirect(self.object.get_absolute_url())
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class WeeklyScheduleDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = CreatorSchedulePattern
    permission_required = "schedules.delete_creatorschedulepattern"
    template_name = "schedules/weekly_schedule_confirm_delete.html"
    page_title = "Eliminar Pauta Recurrente"
    success_url = reverse_lazy("schedules:weekly_list")
    list_url_name = "schedules:weekly_list"

    def get_queryset(self):
        return ScheduleSelector.get_visible_schedule_patterns(user=self.request.user)


# Alias para retrocompatibilidad
SchedulePatternListView = WeeklyScheduleListView
SchedulePatternDetailView = WeeklyScheduleDetailView
SchedulePatternCreateView = WeeklyScheduleCreateView
SchedulePatternUpdateView = WeeklyScheduleUpdateView
SchedulePatternDeleteView = WeeklyScheduleDeleteView
