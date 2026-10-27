from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.schedules.filters import ScheduleExceptionFilter
from rrss_creatos_analyzer.apps.schedules.forms import ScheduleExceptionForm
from rrss_creatos_analyzer.apps.schedules.models import ScheduleException
from rrss_creatos_analyzer.apps.schedules.selectors import ScheduleSelector
from rrss_creatos_analyzer.apps.schedules.services import ScheduleService
from rrss_creatos_analyzer.apps.schedules.tables import ScheduleExceptionTable


class ScheduleExceptionListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = ScheduleException
    permission_required = "schedules.view_scheduleexception"
    table_class = ScheduleExceptionTable
    filterset_class = ScheduleExceptionFilter
    template_name = "schedules/exception_list.html"
    paginate_by = 25
    page_title = "Excepciones y Justificaciones"
    page_subtitle = "Licencias médicas, vacaciones y días de descanso"
    create_url_name = "schedules:exception_create"

    def get_queryset(self):
        return ScheduleSelector.get_visible_exceptions(user=self.request.user)


class ScheduleExceptionDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = ScheduleException
    permission_required = "schedules.view_scheduleexception"
    template_name = "schedules/exception_detail.html"
    page_title = "Detalle de Excepción"
    list_url_name = "schedules:exception_list"
    update_url_name = "schedules:exception_update"
    delete_url_name = "schedules:exception_delete"

    def get_queryset(self):
        return ScheduleSelector.get_visible_exceptions(user=self.request.user)


class ScheduleExceptionCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = ScheduleException
    form_class = ScheduleExceptionForm
    permission_required = "schedules.add_scheduleexception"
    template_name = "schedules/exception_form.html"
    page_title = "Registrar Justificación / Licencia"
    list_url_name = "schedules:exception_list"

    def form_valid(self, form):
        try:
            data = form.cleaned_data
            self.object = ScheduleService.register_exception(
                creator_id=data["creator"].id,
                start_date=data["start_date"],
                end_date=data["end_date"],
                reason_type=data["reason_type"],
                title=data["title"],
                description=data.get("description", ""),
                is_approved=data.get("is_approved", False),
                approved_by=(self.request.user if data.get("is_approved") else None),
                document_url=data.get("document_url", ""),
            )
            messages.success(self.request, "Excepción registrada exitosamente.")
            return redirect(self.object.get_absolute_url())
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class ScheduleExceptionUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = ScheduleException
    form_class = ScheduleExceptionForm
    permission_required = "schedules.change_scheduleexception"
    template_name = "schedules/exception_form.html"
    page_title = "Editar Justificación / Licencia"
    list_url_name = "schedules:exception_list"

    def get_queryset(self):
        return ScheduleSelector.get_visible_exceptions(user=self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Excepción actualizada exitosamente.")
        return redirect(self.object.get_absolute_url())


class ScheduleExceptionDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = ScheduleException
    permission_required = "schedules.delete_scheduleexception"
    template_name = "schedules/exception_confirm_delete.html"
    success_url = reverse_lazy("schedules:exception_list")
    page_title = "Eliminar Excepción"

    def get_queryset(self):
        return ScheduleSelector.get_visible_exceptions(user=self.request.user)


class ScheduleExceptionApproveActionView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    permission_required = "schedules.change_scheduleexception"

    def post(self, request, pk: int):
        ScheduleService.approve_exception(exception_id=pk, approved_by=request.user)
        messages.success(
            request, "Excepción aprobada y slots actualizados a Justificados.",
        )
        return redirect("schedules:exception_detail", pk=pk)
