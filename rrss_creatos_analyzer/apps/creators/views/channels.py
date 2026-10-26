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
    page_title = "Nuevo Canal"
    list_url_name = "creators:channel_list"

    def get_initial(self):
        initial = super().get_initial()
        creator_id = self.request.GET.get("creator")
        if creator_id:
            initial["creator"] = creator_id
        return initial

    def get_success_url(self):
        return reverse("creators:channel_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            self.object = ChannelService.save_channel(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Canal creado exitosamente.")
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
    list_url_name = "creators:channel_list"

    def get_success_url(self):
        return reverse("creators:channel_detail", kwargs={"pk": self.object.pk})

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
    success_url = reverse_lazy("creators:channel_list")
    list_url_name = "creators:channel_list"

    def form_valid(self, form):
        ChannelService.delete_channel(instance=self.get_object())
        messages.success(self.request, "Canal eliminado exitosamente.")
        return redirect(self.success_url)


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
            f"El canal {plat} ha sido marcado como principal.",
        )
        next_url = request.POST.get("next") or reverse(
            "creators:creator_detail",
            kwargs={"pk": channel.creator_id},
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
        next_url = request.POST.get("next") or reverse(
            "creators:creator_detail",
            kwargs={"pk": channel.creator_id},
        )
        return HttpResponseRedirect(next_url)
