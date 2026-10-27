from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError
from rrss_creatos_analyzer.apps.core.mixins import CrudContextMixin
from rrss_creatos_analyzer.apps.creators.filters import ChannelFilter
from rrss_creatos_analyzer.apps.creators.forms import ChannelForm
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.selectors import ChannelSelector
from rrss_creatos_analyzer.apps.creators.selectors import CreatorSelector
from rrss_creatos_analyzer.apps.creators.services import ChannelService
from rrss_creatos_analyzer.apps.creators.tables import ChannelTable


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
    page_title = "Directorio de Canales"
    page_subtitle = (
        "Cuentas oficiales de Twitch, YouTube, Kick, TikTok e Instagram del roster"
    )
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        channel = self.object
        ctx["snapshots"] = channel.snapshots.order_by("-snapshot_date")[:15]
        return ctx


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
    page_title = "Vincular Nuevo Canal"
    page_subtitle = (
        "Asociar cuenta oficial de streaming o video a un talento de la compañía"
    )
    list_url_name = "creators:channel_list"

    def get_initial(self):
        initial = super().get_initial()
        creator_id = self.request.GET.get("creator")
        if creator_id:
            initial["creator"] = creator_id
        return initial

    def get_cancel_url(self):
        creator_id = self.request.GET.get("creator")
        if creator_id:
            return (
                reverse("creators:creator_detail", kwargs={"pk": creator_id})
                + "?tab=channels"
            )
        return reverse("creators:channel_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        creator_id = self.request.GET.get("creator")
        if creator_id:
            ctx["target_creator"] = CreatorSelector.get_by_pk(
                pk=int(creator_id), user=self.request.user
            )
            ctx["cancel_url"] = self.get_cancel_url()
        return ctx

    def get_success_url(self):
        return (
            reverse("creators:creator_detail", kwargs={"pk": self.object.creator_id})
            + "?tab=channels"
        )

    def form_valid(self, form):
        try:
            self.object = ChannelService.save_channel(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(
            self.request,
            f"Canal de {self.object.get_platform_display()} vinculado exitosamente.",
        )
        return redirect(self.get_success_url())


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
    page_title = "Editar Canal"
    page_subtitle = "Modificación de parámetros de sincronización y métricas base"
    list_url_name = "creators:channel_list"

    def get_cancel_url(self):
        return (
            reverse("creators:creator_detail", kwargs={"pk": self.object.creator_id})
            + "?tab=channels"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = self.get_cancel_url()
        return ctx

    def get_success_url(self):
        return (
            reverse("creators:creator_detail", kwargs={"pk": self.object.creator_id})
            + "?tab=channels"
        )

    def form_valid(self, form):
        try:
            self.object = ChannelService.save_channel(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Canal actualizado exitosamente.")
        return redirect(self.get_success_url())


class ChannelDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = Channel
    permission_required = "creators.delete_channel"
    template_name = "creators/channel_confirm_delete.html"
    list_url_name = "creators:channel_list"
    page_title = "Eliminar Canal"

    def get_success_url(self):
        creator_id = self.object.creator_id
        return (
            reverse("creators:creator_detail", kwargs={"pk": creator_id})
            + "?tab=channels"
        )

    def form_valid(self, form):
        self.object = self.get_object()
        creator_id = self.object.creator_id
        plat = self.object.get_platform_display()
        ChannelService.delete_channel(instance=self.object)
        messages.success(self.request, f"Canal {plat} desvinculado exitosamente.")
        return redirect(
            reverse("creators:creator_detail", kwargs={"pk": creator_id})
            + "?tab=channels"
        )


class ChannelSetPrimaryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "creators.change_channel"

    def post(self, request, pk):
        channel = get_object_or_404(
            ChannelSelector.get_visible_queryset(user=request.user),
            pk=pk,
        )
        ChannelService.set_primary_channel(channel=channel)
        plat = channel.get_platform_display()
        messages.success(
            request,
            f"El canal {plat} de {channel.creator.display_name} ha sido fijado como Principal.",
        )
        next_url = request.POST.get("next") or (
            reverse("creators:creator_detail", kwargs={"pk": channel.creator_id})
            + "?tab=channels"
        )
        return HttpResponseRedirect(next_url)


class ChannelToggleSyncView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "creators.change_channel"

    def post(self, request, pk):
        channel = get_object_or_404(
            ChannelSelector.get_visible_queryset(user=request.user),
            pk=pk,
        )
        ChannelService.toggle_sync(channel=channel)
        status_text = "activada" if channel.sync_enabled else "pausada"
        plat = channel.get_platform_display()
        messages.info(
            request,
            f"Sincronización {status_text} para el canal {plat}.",
        )
        next_url = request.POST.get("next") or (
            reverse("creators:creator_detail", kwargs={"pk": channel.creator_id})
            + "?tab=channels"
        )
        return HttpResponseRedirect(next_url)
