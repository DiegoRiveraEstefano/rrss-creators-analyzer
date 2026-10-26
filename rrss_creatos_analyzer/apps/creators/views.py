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

from .filters import ChannelFilter
from .filters import ChannelSnapshotFilter
from .filters import CreatorFilter
from .forms import ChannelForm
from .forms import ChannelSnapshotForm
from .forms import CreatorForm
from .models import Channel
from .models import ChannelSnapshot
from .models import Creator
from .selectors import ChannelSelector
from .selectors import ChannelSnapshotSelector
from .selectors import CreatorSelector
from .services import ChannelService
from .services import ChannelSnapshotService
from .services import CreatorService
from .tables import ChannelSnapshotTable
from .tables import ChannelTable
from .tables import CreatorTable


# ==== CREATOR CRUD ====
class CreatorListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = Creator
    permission_required = "creators.view_creator"
    table_class = CreatorTable
    filterset_class = CreatorFilter
    template_name = "creators/creator_list.html"
    paginate_by = 25
    page_title = "Directorio de Creadores"
    page_subtitle = "Gestión de streamers y talentos de la compañía"
    create_url_name = "creators:creator_create"

    def get_queryset(self):
        return CreatorSelector.get_visible_queryset(user=self.request.user)


class CreatorDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = Creator
    permission_required = "creators.view_creator"
    template_name = "creators/creator_detail.html"
    page_title = "Ficha del Creador"
    list_url_name = "creators:creator_list"
    update_url_name = "creators:creator_update"
    delete_url_name = "creators:creator_delete"

    def get_queryset(self):
        return CreatorSelector.get_visible_queryset(user=self.request.user)


class CreatorCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = Creator
    permission_required = "creators.add_creator"
    form_class = CreatorForm
    template_name = "creators/creator_form.html"
    success_url = reverse_lazy("creators:creator_list")
    page_title = "Registrar Creador"
    list_url_name = "creators:creator_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = CreatorService.save_creator(tags=tags, **data)
        messages.success(self.request, "Creador registrado exitosamente.")
        return redirect(self.success_url)


class CreatorUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = Creator
    permission_required = "creators.change_creator"
    form_class = CreatorForm
    template_name = "creators/creator_form.html"
    success_url = reverse_lazy("creators:creator_list")
    page_title = "Editar Creador"
    list_url_name = "creators:creator_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = CreatorService.save_creator(
            instance=self.get_object(),
            tags=tags,
            **data,
        )
        messages.success(self.request, "Creador actualizado exitosamente.")
        return redirect(self.success_url)


class CreatorDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = Creator
    permission_required = "creators.delete_creator"
    template_name = "creators/creator_confirm_delete.html"
    success_url = reverse_lazy("creators:creator_list")
    list_url_name = "creators:creator_list"

    def form_valid(self, form):
        CreatorService.delete_creator(instance=self.get_object())
        messages.success(self.request, "Creador eliminado.")
        return redirect(self.success_url)


# ==== CHANNEL CRUD ====
class ChannelListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = Channel
    permission_required = "creators.view_channel"
    table_class = ChannelTable
    filterset_class = ChannelFilter
    template_name = "creators/channel_list.html"
    paginate_by = 25
    page_title = "Canales por Plataforma"
    page_subtitle = "Cuentas de Twitch, YouTube, Kick, TikTok e Instagram vinculadas"
    create_url_name = "creators:channel_create"

    def get_queryset(self):
        return ChannelSelector.get_visible_queryset(user=self.request.user)


class ChannelDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = Channel
    permission_required = "creators.view_channel"
    template_name = "creators/channel_detail.html"
    page_title = "Detalle del Canal"
    list_url_name = "creators:channel_list"
    update_url_name = "creators:channel_update"
    delete_url_name = "creators:channel_delete"

    def get_queryset(self):
        return ChannelSelector.get_visible_queryset(user=self.request.user)


class ChannelCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = Channel
    permission_required = "creators.add_channel"
    form_class = ChannelForm
    template_name = "creators/channel_form.html"
    success_url = reverse_lazy("creators:channel_list")
    page_title = "Nuevo Canal"
    list_url_name = "creators:channel_list"

    def form_valid(self, form):
        self.object = ChannelService.save_channel(**form.cleaned_data)
        messages.success(self.request, "Canal creado exitosamente.")
        return redirect(self.success_url)


class ChannelUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = Channel
    permission_required = "creators.change_channel"
    form_class = ChannelForm
    template_name = "creators/channel_form.html"
    success_url = reverse_lazy("creators:channel_list")
    page_title = "Editar Canal"
    list_url_name = "creators:channel_list"

    def form_valid(self, form):
        self.object = ChannelService.save_channel(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Canal actualizado exitosamente.")
        return redirect(self.success_url)


class ChannelDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = Channel
    permission_required = "creators.delete_channel"
    template_name = "creators/channel_confirm_delete.html"
    success_url = reverse_lazy("creators:channel_list")
    list_url_name = "creators:channel_list"

    def form_valid(self, form):
        ChannelService.delete_channel(instance=self.get_object())
        messages.success(self.request, "Canal eliminado.")
        return redirect(self.success_url)


# ==== SNAPSHOT CRUD ====
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
    success_url = reverse_lazy("creators:snapshot_list")
    page_title = "Registrar Snapshot de Canal"
    list_url_name = "creators:snapshot_list"

    def form_valid(self, form):
        self.object = ChannelSnapshotService.save_snapshot(**form.cleaned_data)
        messages.success(self.request, "Snapshot registrado exitosamente.")
        return redirect(self.success_url)


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
    success_url = reverse_lazy("creators:snapshot_list")
    page_title = "Editar Snapshot de Canal"
    list_url_name = "creators:snapshot_list"

    def form_valid(self, form):
        self.object = ChannelSnapshotService.save_snapshot(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Snapshot actualizado exitosamente.")
        return redirect(self.success_url)


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
