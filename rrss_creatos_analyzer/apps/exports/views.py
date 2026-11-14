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

from .filters import ExportJobFilter
from .forms import ExportJobForm
from .models import ExportJob
from .selectors import ExportJobSelector
from .services import ExportJobService
from .tables import ExportJobTable


class ExportJobListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = ExportJob
    permission_required = "exports.view_exportjob"
    table_class = ExportJobTable
    filterset_class = ExportJobFilter
    template_name = "exports/export_list.html"
    paginate_by = 25
    page_title = "Trabajos de Exportación"
    create_url_name = "exports:export_create"

    def get_queryset(self):
        return ExportJobSelector.get_queryset()


class ExportJobDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = ExportJob
    permission_required = "exports.view_exportjob"
    template_name = "exports/export_detail.html"
    page_title = "Detalle de Trabajo de Exportación"
    list_url_name = "exports:export_list"
    update_url_name = "exports:export_update"
    delete_url_name = "exports:export_delete"


@method_decorator(
    ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True),
    name="dispatch",
)
class ExportJobCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = ExportJob
    permission_required = "exports.add_exportjob"
    form_class = ExportJobForm
    template_name = "exports/export_form.html"
    success_url = reverse_lazy("exports:export_list")
    page_title = "Crear Trabajo de Exportación"
    list_url_name = "exports:export_list"

    def form_valid(self, form):
        self.object = ExportJobService.save_record(**form.cleaned_data)
        messages.success(self.request, "Registro guardado exitosamente.")
        return redirect(self.success_url)


class ExportJobUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = ExportJob
    permission_required = "exports.change_exportjob"
    form_class = ExportJobForm
    template_name = "exports/export_form.html"
    success_url = reverse_lazy("exports:export_list")
    page_title = "Editar Trabajo de Exportación"
    list_url_name = "exports:export_list"

    def form_valid(self, form):
        self.object = ExportJobService.save_record(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Registro actualizado exitosamente.")
        return redirect(self.success_url)


class ExportJobDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = ExportJob
    permission_required = "exports.delete_exportjob"
    template_name = "exports/export_confirm_delete.html"
    success_url = reverse_lazy("exports:export_list")
    list_url_name = "exports:export_list"

    def form_valid(self, form):
        ExportJobService.delete_record(instance=self.get_object())
        messages.success(self.request, "Registro eliminado.")
        return redirect(self.success_url)
