from __future__ import annotations

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
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import ChannelSnapshot
from rrss_creatos_analyzer.apps.creators.selectors import ChannelSelector
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
    page_title = "Histórico de Snapshots de Audiencia"
    page_subtitle = "Registro diario de seguidores, suscriptores y visualizaciones"
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
    page_title = "Registrar Snapshot de Audiencia"
    page_subtitle = (
        "Captura métricas del día (las variaciones delta se calculan automáticamente)"
    )
    list_url_name = "creators:snapshot_list"

    def get_initial(self):
        initial = super().get_initial()
        channel_id = self.request.GET.get("channel")
        if channel_id:
            initial["channel"] = channel_id
            channel = ChannelSelector.get_by_pk(
                pk=int(channel_id), user=self.request.user
            )
            if channel:
                initial["followers_count"] = channel.followers_count
                initial["subscribers_count"] = channel.subscribers_count
                initial["paid_subscribers_count"] = channel.paid_subscribers_count
                initial["total_views_count"] = channel.total_views_count
        return initial

    def get_cancel_url(self):
        channel_id = self.request.GET.get("channel")
        if channel_id:
            channel = ChannelSelector.get_by_pk(
                pk=int(channel_id), user=self.request.user
            )
            if channel:
                return (
                    reverse(
                        "creators:creator_detail", kwargs={"pk": channel.creator_id}
                    )
                    + "?tab=growth"
                )
        return reverse("creators:snapshot_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = self.get_cancel_url()
        return ctx

    def get_success_url(self):
        return (
            reverse(
                "creators:creator_detail",
                kwargs={"pk": self.object.channel.creator_id},
            )
            + "?tab=growth"
        )

    def form_valid(self, form):
        try:
            self.object = ChannelSnapshotService.save_snapshot(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(
            self.request,
            f"Snapshot de {self.object.channel} para {self.object.snapshot_date} guardado exitosamente.",
        )
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
    page_title = "Editar Snapshot de Audiencia"
    page_subtitle = "Ajuste manual de registros de métricas o variaciones"
    list_url_name = "creators:snapshot_list"

    def get_cancel_url(self):
        return (
            reverse(
                "creators:creator_detail",
                kwargs={"pk": self.object.channel.creator_id},
            )
            + "?tab=growth"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = self.get_cancel_url()
        return ctx

    def get_success_url(self):
        return (
            reverse(
                "creators:creator_detail",
                kwargs={"pk": self.object.channel.creator_id},
            )
            + "?tab=growth"
        )

    def form_valid(self, form):
        try:
            self.object = ChannelSnapshotService.save_snapshot(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Snapshot actualizado correctamente.")
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
    list_url_name = "creators:snapshot_list"
    page_title = "Eliminar Registro de Snapshot"

    def get_success_url(self):
        creator_id = self.object.channel.creator_id
        return (
            reverse("creators:creator_detail", kwargs={"pk": creator_id})
            + "?tab=growth"
        )

    def form_valid(self, form):
        self.object = self.get_object()
        creator_id = self.object.channel.creator_id
        ChannelSnapshotService.delete_snapshot(instance=self.object)
        messages.success(self.request, "Snapshot eliminado del histórico.")
        return redirect(
            reverse("creators:creator_detail", kwargs={"pk": creator_id})
            + "?tab=growth"
        )
