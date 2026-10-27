from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.editors.forms import TaskRevisionForm
from rrss_creatos_analyzer.apps.editors.models import EditingTask
from rrss_creatos_analyzer.apps.editors.models import TaskRevision
from rrss_creatos_analyzer.apps.editors.selectors import TaskRevisionSelector
from rrss_creatos_analyzer.apps.editors.services import TaskRevisionService


class TaskRevisionDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = TaskRevision
    permission_required = "editors.view_taskrevision"
    template_name = "editors/revision_detail.html"
    page_title = "Detalle de Revisión de Corte"

    def get_queryset(self):
        return TaskRevisionSelector.get_visible_queryset(user=self.request.user)


class TaskRevisionCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = TaskRevision
    permission_required = "editors.add_taskrevision"
    form_class = TaskRevisionForm
    template_name = "editors/revision_form.html"
    page_title = "Enviar Corte / Versión a Revisión"

    def get_initial(self):
        initial = super().get_initial()
        task_id = self.kwargs.get("task_id")
        if task_id:
            task = get_object_or_404(EditingTask, pk=task_id)
            initial["task"] = task
            initial["revision_number"] = task.revision_count + 1
        return initial

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        try:
            self.object = TaskRevisionService.save_revision(**data)
            messages.success(self.request, "Versión de corte enviada a revisión.")
            return redirect(
                reverse("editors:task_detail", kwargs={"pk": self.object.task_id}),
            )
        except BusinessLogicError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
