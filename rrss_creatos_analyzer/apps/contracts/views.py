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

from .filters import ContractFilter
from .forms import ContractForm
from .models import Contract
from .selectors import ContractSelector
from .services import ContractService
from .tables import ContractTable


class ContractListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = Contract
    permission_required = "contracts.view_contract"
    table_class = ContractTable
    filterset_class = ContractFilter
    template_name = "contracts/contract_list.html"
    paginate_by = 25
    page_title = "Contratos y Acuerdos de Talento"
    page_subtitle = "Gestión de revenue splits, retainers y cuotas mensuales"
    create_url_name = "contracts:contract_create"

    def get_queryset(self):
        return ContractSelector.get_visible_queryset(user=self.request.user)


class ContractDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = Contract
    permission_required = "contracts.view_contract"
    template_name = "contracts/contract_detail.html"
    page_title = "Detalle de Contrato"
    list_url_name = "contracts:contract_list"
    update_url_name = "contracts:contract_update"
    delete_url_name = "contracts:contract_delete"

    def get_queryset(self):
        return ContractSelector.get_visible_queryset(user=self.request.user)


class ContractCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = Contract
    permission_required = "contracts.add_contract"
    form_class = ContractForm
    template_name = "contracts/contract_form.html"
    success_url = reverse_lazy("contracts:contract_list")
    page_title = "Nuevo Contrato"
    list_url_name = "contracts:contract_list"

    def form_valid(self, form):
        try:
            self.object = ContractService.save_contract(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Contrato creado exitosamente.")
        return redirect(self.success_url)


class ContractUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = Contract
    permission_required = "contracts.change_contract"
    form_class = ContractForm
    template_name = "contracts/contract_form.html"
    success_url = reverse_lazy("contracts:contract_list")
    page_title = "Editar Contrato"
    list_url_name = "contracts:contract_list"

    def form_valid(self, form):
        try:
            self.object = ContractService.save_contract(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Contrato actualizado exitosamente.")
        return redirect(self.success_url)


class ContractDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = Contract
    permission_required = "contracts.delete_contract"
    template_name = "contracts/contract_confirm_delete.html"
    success_url = reverse_lazy("contracts:contract_list")
    list_url_name = "contracts:contract_list"

    def form_valid(self, form):
        ContractService.delete_contract(instance=self.get_object())
        messages.success(self.request, "Contrato eliminado.")
        return redirect(self.success_url)
