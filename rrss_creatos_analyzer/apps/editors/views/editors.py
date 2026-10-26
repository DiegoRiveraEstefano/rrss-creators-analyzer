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
from rrss_creatos_analyzer.apps.editors.filters import EditorFilter
from rrss_creatos_analyzer.apps.editors.forms import EditorForm
from rrss_creatos_analyzer.apps.editors.models import Editor
from rrss_creatos_analyzer.apps.editors.selectors import EditorSelector
from rrss_creatos_analyzer.apps.editors.services import EditorService
from rrss_creatos_analyzer.apps.editors.tables import EditorTable


class EditorListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = Editor
    permission_required = "editors.view_editor"
    table_class = EditorTable
    filterset_class = EditorFilter
    template_name = "editors/editor_list.html"
    paginate_by = 25
    page_title = "Editores y Postproducción"
    page_subtitle = (
        "Gestión de editores de video, diseñadores y equipo de postproducción"
    )
    create_url_name = "editors:editor_create"

    def get_queryset(self):
        return EditorSelector.get_visible_queryset(user=self.request.user)


class EditorDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = Editor
    permission_required = "editors.view_editor"
    template_name = "editors/editor_detail.html"
    page_title = "Perfil de Editor"
    list_url_name = "editors:editor_list"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return EditorSelector.get_visible_queryset(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["metrics"] = EditorSelector.get_editor_metrics(editor_id=self.object.id)
        ctx["active_assignments"] = self.object.assignments.filter(
            status="active",
        ).select_related("creator")
        ctx["recent_tasks"] = self.object.editing_tasks.select_related(
            "creator",
            "video",
        )[:10]
        return ctx


class EditorCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = Editor
    permission_required = "editors.add_editor"
    form_class = EditorForm
    template_name = "editors/editor_form.html"
    success_url = reverse_lazy("editors:editor_list")
    page_title = "Nuevo Editor"
    page_subtitle = "Registrar un nuevo editor en el equipo o red de talento"
    list_url_name = "editors:editor_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        try:
            self.object = EditorService.save_editor(tags=tags, **data)
            messages.success(self.request, "Editor registrado exitosamente.")
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class EditorUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = Editor
    permission_required = "editors.change_editor"
    form_class = EditorForm
    template_name = "editors/editor_form.html"
    success_url = reverse_lazy("editors:editor_list")
    page_title = "Editar Editor"
    list_url_name = "editors:editor_list"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        try:
            self.object = EditorService.save_editor(
                instance=self.get_object(),
                tags=tags,
                **data,
            )
            messages.success(self.request, "Editor actualizado exitosamente.")
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class EditorDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = Editor
    permission_required = "editors.delete_editor"
    template_name = "editors/editor_confirm_delete.html"
    success_url = reverse_lazy("editors:editor_list")
    list_url_name = "editors:editor_list"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        try:
            EditorService.delete_editor(instance=self.get_object())
            messages.success(self.request, "Editor eliminado exitosamente.")
            return redirect(self.success_url)
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return redirect(self.get_object().get_absolute_url())
