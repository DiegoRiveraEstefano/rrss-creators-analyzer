from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.creators.filters import ChannelSnapshotFilter
from rrss_creatos_analyzer.apps.creators.forms import ChannelSnapshotForm
from rrss_creatos_analyzer.apps.creators.models import ChannelSnapshot
from rrss_creatos_analyzer.apps.creators.selectors import ChannelSnapshotSelector
from rrss_creatos_analyzer.apps.creators.services import ChannelSnapshotService
from rrss_creatos_analyzer.apps.creators.tables import ChannelSnapshotTable


class ChannelSnapshotListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = ChannelSnapshot
    permission_required = "creators.view_channelsnapshot"
    table_class = ChannelSnapshotTable
    filterset_class = ChannelSnapshotFilter
    template_name = "creators/snapshot_list.html"
    paginate_by = 25
    page_title = "Snapshots de Crecimiento de Canales"
    create_url_name = "creators:snapshot_create"

    def get_queryset(self):
        return ChannelSnapshotSelector.get_visible_queryset(user=self.request.user)


class ChannelSnapshotDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = ChannelSnapshot
    permission_required = "creators.view_channelsnapshot"
    template_name = "creators/snapshot_detail.html"
    page_title = "Detalle de Snapshot"
    list_url_name = "creators:snapshot_list"
    update_url_name = "creators:snapshot_update"
    delete_url_name = "creators:snapshot_delete"

    def get_queryset(self):
        return ChannelSnapshotSelector.get_visible_queryset(user=self.request.user)


class ChannelSnapshotCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = ChannelSnapshot
    permission_required = "creators.add_channelsnapshot"
    form_class = ChannelSnapshotForm
    template_name = "creators/snapshot_form.html"
    page_title = "Registrar Snapshot de Canal"
    list_url_name = "creators:snapshot_list"

    def get_success_url(self):
        return reverse("creators:snapshot_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            self.object = ChannelSnapshotService.save_snapshot(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Snapshot registrado exitosamente.")
        return redirect(self.get_success_url())


class ChannelSnapshotUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = ChannelSnapshot
    permission_required = "creators.change_channelsnapshot"
    form_class = ChannelSnapshotForm
    template_name = "creators/snapshot_form.html"
    page_title = "Editar Snapshot de Canal"
    list_url_name = "creators:snapshot_list"

    def get_success_url(self):
        return reverse("creators:snapshot_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            self.object = ChannelSnapshotService.save_snapshot(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Snapshot actualizado exitosamente.")
        return redirect(self.get_success_url())


class ChannelSnapshotDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = ChannelSnapshot
    permission_required = "creators.delete_channelsnapshot"
    template_name = "creators/snapshot_confirm_delete.html"
    success_url = reverse_lazy("creators:snapshot_list")
    list_url_name = "creators:snapshot_list"

    def form_valid(self, form):
        ChannelSnapshotService.delete_snapshot(instance=self.get_object())
        messages.success(self.request, "Snapshot eliminado.")
        return redirect(self.success_url)
