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

from .filters import AnalyticsSnapshotFilter
from .forms import AnalyticsSnapshotForm
from .models import AnalyticsSnapshot
from .selectors import AnalyticsSnapshotSelector
from .services import AnalyticsSnapshotService
from .tables import AnalyticsSnapshotTable


class AnalyticsSnapshotListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = AnalyticsSnapshot
    permission_required = "analytics.view_analyticssnapshot"
    table_class = AnalyticsSnapshotTable
    filterset_class = AnalyticsSnapshotFilter
    template_name = "analytics/snapshot_list.html"
    paginate_by = 25
    page_title = "Snapshots Analíticos (DiskCache)"
    create_url_name = "analytics:snapshot_create"

    def get_queryset(self):
        return AnalyticsSnapshotSelector.get_queryset()


class AnalyticsSnapshotDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = AnalyticsSnapshot
    permission_required = "analytics.view_analyticssnapshot"
    template_name = "analytics/snapshot_detail.html"
    page_title = "Detalle de Snapshot Analítico (DiskCache)"
    list_url_name = "analytics:snapshot_list"
    update_url_name = "analytics:snapshot_update"
    delete_url_name = "analytics:snapshot_delete"


class AnalyticsSnapshotCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = AnalyticsSnapshot
    permission_required = "analytics.add_analyticssnapshot"
    form_class = AnalyticsSnapshotForm
    template_name = "analytics/snapshot_form.html"
    success_url = reverse_lazy("analytics:snapshot_list")
    page_title = "Crear Snapshot Analítico (DiskCache)"
    list_url_name = "analytics:snapshot_list"

    def form_valid(self, form):
        self.object = AnalyticsSnapshotService.save_record(**form.cleaned_data)
        messages.success(self.request, "Registro guardado exitosamente.")
        return redirect(self.success_url)


class AnalyticsSnapshotUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = AnalyticsSnapshot
    permission_required = "analytics.change_analyticssnapshot"
    form_class = AnalyticsSnapshotForm
    template_name = "analytics/snapshot_form.html"
    success_url = reverse_lazy("analytics:snapshot_list")
    page_title = "Editar Snapshot Analítico (DiskCache)"
    list_url_name = "analytics:snapshot_list"

    def form_valid(self, form):
        self.object = AnalyticsSnapshotService.save_record(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Registro actualizado exitosamente.")
        return redirect(self.success_url)


class AnalyticsSnapshotDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = AnalyticsSnapshot
    permission_required = "analytics.delete_analyticssnapshot"
    template_name = "analytics/snapshot_confirm_delete.html"
    success_url = reverse_lazy("analytics:snapshot_list")
    list_url_name = "analytics:snapshot_list"

    def form_valid(self, form):
        AnalyticsSnapshotService.delete_record(instance=self.get_object())
        messages.success(self.request, "Registro eliminado.")
        return redirect(self.success_url)
