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
from rrss_creatos_analyzer.apps.editors.filters import EditingTaskFilter
from rrss_creatos_analyzer.apps.editors.forms import EditingTaskForm
from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.selectors import EditingTaskSelector
from rrss_creatos_analyzer.apps.editors.services import EditingTaskService
from rrss_creatos_analyzer.apps.editors.tables import EditingTaskTable


class EditingTaskListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = EditingTask
    permission_required = "editors.view_editingtask"
    table_class = EditingTaskTable
    filterset_class = EditingTaskFilter
    template_name = "editors/task_list.html"
    paginate_by = 25
    page_title = "Tareas de Edición"
    page_subtitle = (
        "Control de proyectos, entregas, revisiones y liquidación de editores"
    )
    create_url_name = "editors:task_create"

    def get_queryset(self):
        return EditingTaskSelector.get_visible_queryset(user=self.request.user)


class EditingTaskDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = EditingTask
    permission_required = "editors.view_editingtask"
    template_name = "editors/task_detail.html"
    page_title = "Detalle de Tarea de Edición"
    list_url_name = "editors:task_list"

    def get_queryset(self):
        return EditingTaskSelector.get_visible_queryset(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["revisions"] = self.object.revisions.all()
        return ctx


class EditingTaskCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = EditingTask
    permission_required = "editors.add_editingtask"
    form_class = EditingTaskForm
    template_name = "editors/task_form.html"
    success_url = reverse_lazy("editors:task_list")
    page_title = "Nueva Tarea de Edición"
    list_url_name = "editors:task_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        try:
            self.object = EditingTaskService.create_task(tags=tags, **data)
            messages.success(
                self.request,
                "Tarea de edición creada y asignada exitosamente.",
            )
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class EditingTaskUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = EditingTask
    permission_required = "editors.change_editingtask"
    form_class = EditingTaskForm
    template_name = "editors/task_form.html"
    success_url = reverse_lazy("editors:task_list")
    page_title = "Editar Tarea de Edición"
    list_url_name = "editors:task_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        try:
            self.object = EditingTaskService.update_task(
                instance=self.get_object(),
                tags=tags,
                **data,
            )
            messages.success(self.request, "Tarea de edición actualizada.")
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class EditingTaskDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = EditingTask
    permission_required = "editors.delete_editingtask"
    template_name = "editors/task_confirm_delete.html"
    success_url = reverse_lazy("editors:task_list")
    list_url_name = "editors:task_list"

    def form_valid(self, form):
        EditingTaskService.delete_task(instance=self.get_object())
        messages.success(self.request, "Tarea eliminada exitosamente.")
        return redirect(self.success_url)
