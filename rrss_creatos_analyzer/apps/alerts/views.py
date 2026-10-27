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

from .filters import ChannelAlertFilter
from .forms import ChannelAlertForm
from .models import ChannelAlert
from .selectors import ChannelAlertSelector
from .services import ChannelAlertService
from .tables import ChannelAlertTable


class ChannelAlertListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = ChannelAlert
    permission_required = "alerts.view_channelalert"
    table_class = ChannelAlertTable
    filterset_class = ChannelAlertFilter
    template_name = "alerts/alert_list.html"
    paginate_by = 25
    page_title = "Alertas, Strikes y Anomalías de Canal"
    page_subtitle = (
        "Seguimiento de sanciones DMCA, violaciones TOS y alertas de rendimiento"
    )
    create_url_name = "alerts:alert_create"

    def get_queryset(self):
        return ChannelAlertSelector.get_visible_queryset(user=self.request.user)


class ChannelAlertDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = ChannelAlert
    permission_required = "alerts.view_channelalert"
    template_name = "alerts/alert_detail.html"
    page_title = "Detalle de Alerta de Canal"
    list_url_name = "alerts:alert_list"
    update_url_name = "alerts:alert_update"
    delete_url_name = "alerts:alert_delete"

    def get_queryset(self):
        return ChannelAlertSelector.get_visible_queryset(user=self.request.user)


class ChannelAlertCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = ChannelAlert
    permission_required = "alerts.add_channelalert"
    form_class = ChannelAlertForm
    template_name = "alerts/alert_form.html"
    success_url = reverse_lazy("alerts:alert_list")
    page_title = "Registrar Alerta / Strike"
    list_url_name = "alerts:alert_list"

    def form_valid(self, form):
        self.object = ChannelAlertService.save_alert(**form.cleaned_data)
        messages.success(self.request, "Alerta registrada exitosamente.")
        return redirect(self.success_url)


class ChannelAlertUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = ChannelAlert
    permission_required = "alerts.change_channelalert"
    form_class = ChannelAlertForm
    template_name = "alerts/alert_form.html"
    success_url = reverse_lazy("alerts:alert_list")
    page_title = "Editar Alerta / Strike"
    list_url_name = "alerts:alert_list"

    def form_valid(self, form):
        self.object = ChannelAlertService.save_alert(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Alerta actualizada exitosamente.")
        return redirect(self.success_url)


class ChannelAlertDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = ChannelAlert
    permission_required = "alerts.delete_channelalert"
    template_name = "alerts/alert_confirm_delete.html"
    success_url = reverse_lazy("alerts:alert_list")
    list_url_name = "alerts:alert_list"

    def form_valid(self, form):
        ChannelAlertService.delete_alert(instance=self.get_object())
        messages.success(self.request, "Alerta eliminada.")
        return redirect(self.success_url)
