from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_ratelimit.decorators import ratelimit
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin

from .filters import ImportBatchFilter
from .forms import ImportBatchForm
from .models import ImportBatch
from .selectors import ImportBatchSelector
from .services import ImportBatchService
from .tables import ImportBatchTable


class ImportBatchListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = ImportBatch
    permission_required = "imports.view_importbatch"
    table_class = ImportBatchTable
    filterset_class = ImportBatchFilter
    template_name = "imports/batch_list.html"
    paginate_by = 25
    page_title = "Lotes de Importación"
    page_subtitle = "Historial y auditoría de cargas masivas CSV / XLSX"
    create_url_name = "imports:batch_create"

    def get_queryset(self):
        return ImportBatchSelector.get_queryset()


class ImportBatchDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = ImportBatch
    permission_required = "imports.view_importbatch"
    template_name = "imports/batch_detail.html"
    page_title = "Detalle de Lote de Importación"
    list_url_name = "imports:batch_list"
    update_url_name = "imports:batch_update"
    delete_url_name = "imports:batch_delete"


@method_decorator(
    ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True),
    name="dispatch",
)
class ImportBatchCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = ImportBatch
    permission_required = "imports.add_importbatch"
    form_class = ImportBatchForm
    template_name = "imports/batch_form.html"
    success_url = reverse_lazy("imports:batch_list")
    page_title = "Registrar Lote de Importación"
    list_url_name = "imports:batch_list"

    def form_valid(self, form):
        self.object = ImportBatchService.save_batch(
            uploaded_by=self.request.user,
            **form.cleaned_data,
        )
        messages.success(self.request, "Lote registrado exitosamente.")
        return redirect(self.success_url)


class ImportBatchUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = ImportBatch
    permission_required = "imports.change_importbatch"
    form_class = ImportBatchForm
    template_name = "imports/batch_form.html"
    success_url = reverse_lazy("imports:batch_list")
    page_title = "Editar Lote de Importación"
    list_url_name = "imports:batch_list"

    def form_valid(self, form):
        self.object = ImportBatchService.save_batch(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Lote actualizado exitosamente.")
        return redirect(self.success_url)


class ImportBatchDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = ImportBatch
    permission_required = "imports.delete_importbatch"
    template_name = "imports/batch_confirm_delete.html"
    success_url = reverse_lazy("imports:batch_list")
    list_url_name = "imports:batch_list"

    def form_valid(self, form):
        ImportBatchService.delete_batch(instance=self.get_object())
        messages.success(self.request, "Lote eliminado.")
        return redirect(self.success_url)
