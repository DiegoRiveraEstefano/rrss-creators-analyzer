from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.schedules.filters import CreatorScheduleSlotFilter
from rrss_creatos_analyzer.apps.schedules.forms import CreatorScheduleSlotForm
from rrss_creatos_analyzer.apps.schedules.forms import GenerateSlotsForm
from rrss_creatos_analyzer.apps.schedules.models import CreatorScheduleSlot
from rrss_creatos_analyzer.apps.schedules.selectors import ScheduleSelector
from rrss_creatos_analyzer.apps.schedules.services import ScheduleService
from rrss_creatos_analyzer.apps.schedules.tables import CreatorScheduleSlotTable


class ScheduleSlotListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = CreatorScheduleSlot
    permission_required = "schedules.view_creatorscheduleslot"
    table_class = CreatorScheduleSlotTable
    filterset_class = CreatorScheduleSlotFilter
    template_name = "schedules/slot_list.html"
    paginate_by = 25
    page_title = "Slots de Transmisión Programados"
    page_subtitle = "Seguimiento y conciliación de citas de emisión"
    create_url_name = "schedules:slot_create"

    def get_queryset(self):
        return ScheduleSelector.get_visible_slots(user=self.request.user)


class ScheduleSlotDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = CreatorScheduleSlot
    permission_required = "schedules.view_creatorscheduleslot"
    template_name = "schedules/slot_detail.html"
    page_title = "Detalle de Slot Programado"
    list_url_name = "schedules:slot_list"
    update_url_name = "schedules:slot_update"
    delete_url_name = "schedules:slot_delete"

    def get_queryset(self):
        return ScheduleSelector.get_visible_slots(user=self.request.user)


class ScheduleSlotCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = CreatorScheduleSlot
    form_class = CreatorScheduleSlotForm
    permission_required = "schedules.add_creatorscheduleslot"
    template_name = "schedules/slot_form.html"
    page_title = "Nuevo Slot de Transmisión"
    list_url_name = "schedules:slot_list"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Slot programado creado exitosamente.")
        return redirect(self.object.get_absolute_url())


class ScheduleSlotUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = CreatorScheduleSlot
    form_class = CreatorScheduleSlotForm
    permission_required = "schedules.change_creatorscheduleslot"
    template_name = "schedules/slot_form.html"
    page_title = "Editar Slot de Transmisión"
    list_url_name = "schedules:slot_list"

    def get_queryset(self):
        return ScheduleSelector.get_visible_slots(user=self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Slot programado actualizado exitosamente.")
        return redirect(self.object.get_absolute_url())


class ScheduleSlotDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = CreatorScheduleSlot
    permission_required = "schedules.delete_creatorscheduleslot"
    template_name = "schedules/slot_confirm_delete.html"
    success_url = reverse_lazy("schedules:slot_list")
    page_title = "Eliminar Slot Programado"

    def get_queryset(self):
        return ScheduleSelector.get_visible_slots(user=self.request.user)


class ScheduleSlotReconcileActionView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    permission_required = "schedules.change_creatorscheduleslot"

    def post(self, request, pk: int):
        slot = get_object_or_404(
            ScheduleSelector.get_visible_slots(user=request.user), pk=pk,
        )
        ScheduleService.reconcile_slot(slot=slot)
        messages.success(
            request, f"Slot conciliado. Nuevo estado: {slot.get_status_display()}",
        )
        return redirect(slot.get_absolute_url())


class GenerateSlotsView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    FormView,
):
    form_class = GenerateSlotsForm
    permission_required = "schedules.add_creatorscheduleslot"
    template_name = "schedules/generate_slots_form.html"
    page_title = "Generar Slots de Calendario"
    page_subtitle = "Proyectar pautas semanales en un rango de fechas"
    success_url = reverse_lazy("schedules:slot_list")

    def form_valid(self, form):
        data = form.cleaned_data
        creator = data.get("creator")
        count = ScheduleService.generate_slots_for_period(
            start_date=data["start_date"],
            end_date=data["end_date"],
            creator_id=creator.id if creator else None,
        )
        messages.success(
            self.request, f"Se generaron exitosamente {count} slots de agenda.",
        )
        return super().form_valid(form)
