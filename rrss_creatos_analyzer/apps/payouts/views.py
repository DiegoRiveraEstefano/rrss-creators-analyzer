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

from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin

from .filters import CreatorPayoutFilter
from .forms import CreatorPayoutForm
from .models import CreatorPayout
from .selectors import CreatorPayoutSelector
from .services import CreatorPayoutService
from .tables import CreatorPayoutTable


class CreatorPayoutListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = CreatorPayout
    permission_required = "payouts.view_creatorpayout"
    table_class = CreatorPayoutTable
    filterset_class = CreatorPayoutFilter
    template_name = "payouts/payout_list.html"
    paginate_by = 25
    page_title = "Liquidaciones Mensuales a Creadores"
    page_subtitle = (
        "Control financiero de ingresos brutos, comisiones de agencia y pagos netos"
    )
    create_url_name = "payouts:payout_create"

    def get_queryset(self):
        return CreatorPayoutSelector.get_visible_queryset(user=self.request.user)


class CreatorPayoutDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = CreatorPayout
    permission_required = "payouts.view_creatorpayout"
    template_name = "payouts/payout_detail.html"
    page_title = "Detalle de Liquidación"
    list_url_name = "payouts:payout_list"
    update_url_name = "payouts:payout_update"
    delete_url_name = "payouts:payout_delete"

    def get_queryset(self):
        return CreatorPayoutSelector.get_visible_queryset(user=self.request.user)


class CreatorPayoutCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = CreatorPayout
    permission_required = "payouts.add_creatorpayout"
    form_class = CreatorPayoutForm
    template_name = "payouts/payout_form.html"
    success_url = reverse_lazy("payouts:payout_list")
    page_title = "Generar Liquidación Mensual"
    list_url_name = "payouts:payout_list"

    def form_valid(self, form):
        self.object = CreatorPayoutService.save_payout(**form.cleaned_data)
        messages.success(self.request, "Liquidación registrada exitosamente.")
        return redirect(self.success_url)


class CreatorPayoutUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = CreatorPayout
    permission_required = "payouts.change_creatorpayout"
    form_class = CreatorPayoutForm
    template_name = "payouts/payout_form.html"
    success_url = reverse_lazy("payouts:payout_list")
    page_title = "Editar Liquidación Mensual"
    list_url_name = "payouts:payout_list"

    def form_valid(self, form):
        self.object = CreatorPayoutService.save_payout(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Liquidación actualizada exitosamente.")
        return redirect(self.success_url)


class CreatorPayoutDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = CreatorPayout
    permission_required = "payouts.delete_creatorpayout"
    template_name = "payouts/payout_confirm_delete.html"
    success_url = reverse_lazy("payouts:payout_list")
    list_url_name = "payouts:payout_list"

    def form_valid(self, form):
        CreatorPayoutService.delete_payout(instance=self.get_object())
        messages.success(self.request, "Liquidación eliminada.")
        return redirect(self.success_url)
