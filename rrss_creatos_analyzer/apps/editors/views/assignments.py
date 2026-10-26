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
from rrss_creatos_analyzer.apps.editors.filters import EditorAssignmentFilter
from rrss_creatos_analyzer.apps.editors.forms import EditorAssignmentForm
from rrss_creatos_analyzer.apps.editors.models import EditorAssignment
from rrss_creatos_analyzer.apps.editors.selectors import EditorAssignmentSelector
from rrss_creatos_analyzer.apps.editors.services import EditorAssignmentService
from rrss_creatos_analyzer.apps.editors.tables import EditorAssignmentTable


class EditorAssignmentListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = EditorAssignment
    permission_required = "editors.view_editorassignment"
    table_class = EditorAssignmentTable
    filterset_class = EditorAssignmentFilter
    template_name = "editors/assignment_list.html"
    paginate_by = 25
    page_title = "Asignaciones de Editores"
    page_subtitle = "Asignación operativa de editores y tarifas pactadas por creador"
    create_url_name = "editors:assignment_create"

    def get_queryset(self):
        return EditorAssignmentSelector.get_visible_queryset(user=self.request.user)


class EditorAssignmentDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = EditorAssignment
    permission_required = "editors.view_editorassignment"
    template_name = "editors/assignment_detail.html"
    page_title = "Detalle de Asignación"
    list_url_name = "editors:assignment_list"

    def get_queryset(self):
        return EditorAssignmentSelector.get_visible_queryset(user=self.request.user)


class EditorAssignmentCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = EditorAssignment
    permission_required = "editors.add_editorassignment"
    form_class = EditorAssignmentForm
    template_name = "editors/assignment_form.html"
    success_url = reverse_lazy("editors:assignment_list")
    page_title = "Nueva Asignación de Editor"
    list_url_name = "editors:assignment_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        try:
            self.object = EditorAssignmentService.save_assignment(**data)
            messages.success(self.request, "Asignación creada exitosamente.")
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class EditorAssignmentUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = EditorAssignment
    permission_required = "editors.change_editorassignment"
    form_class = EditorAssignmentForm
    template_name = "editors/assignment_form.html"
    success_url = reverse_lazy("editors:assignment_list")
    page_title = "Editar Asignación de Editor"
    list_url_name = "editors:assignment_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        try:
            self.object = EditorAssignmentService.save_assignment(
                instance=self.get_object(),
                **data,
            )
            messages.success(self.request, "Asignación actualizada exitosamente.")
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class EditorAssignmentDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = EditorAssignment
    permission_required = "editors.delete_editorassignment"
    template_name = "editors/assignment_confirm_delete.html"
    success_url = reverse_lazy("editors:assignment_list")
    list_url_name = "editors:assignment_list"

    def form_valid(self, form):
        EditorAssignmentService.delete_assignment(instance=self.get_object())
        messages.success(self.request, "Asignación eliminada exitosamente.")
        return redirect(self.success_url)
