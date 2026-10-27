from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
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
from rrss_creatos_analyzer.apps.creators.filters import CreatorFilter
from rrss_creatos_analyzer.apps.creators.forms import ChannelForm
from rrss_creatos_analyzer.apps.creators.forms import ChannelSnapshotForm
from rrss_creatos_analyzer.apps.creators.forms import CreatorForm
from rrss_creatos_analyzer.apps.creators.forms import CreatorPersonalInfoForm
from rrss_creatos_analyzer.apps.creators.forms import CreatorStatusChangeForm
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.creators.models import CreatorPersonalInfo
from rrss_creatos_analyzer.apps.creators.selectors import ChannelSelector
from rrss_creatos_analyzer.apps.creators.selectors import CreatorSelector
from rrss_creatos_analyzer.apps.creators.services import CreatorService
from rrss_creatos_analyzer.apps.creators.tables import CreatorTable


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
    page_subtitle = "Gestión integral de streamers, talentos y canales de la agencia"
    create_url_name = "creators:creator_create"

    def get_queryset(self):
        return CreatorSelector.get_visible_queryset(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["kpis"] = CreatorSelector.get_kpis(user=self.request.user)
        return ctx


class CreatorDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = Creator
    permission_required = "creators.view_creator"
    template_name = "creators/creator_detail.html"
    page_title = "Ficha 360° del Creador"
    list_url_name = "creators:creator_list"
    update_url_name = "creators:creator_update"
    delete_url_name = "creators:creator_delete"

    def get_queryset(self):
        return CreatorSelector.get_visible_queryset(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        creator = self.object

        # Contexto analítico y operativo 360°
        context_360 = CreatorSelector.get_360_context(
            creator=creator,
            user=self.request.user,
        )
        ctx.update(context_360)

        # Formularios rápidos para modales interactivos
        ctx["status_form"] = CreatorStatusChangeForm(
            initial={"status": creator.status},
        )
        ctx["quick_channel_form"] = ChannelForm(
            initial={"creator": creator.pk, "is_monetized": True, "sync_enabled": True},
        )
        ctx["active_tab"] = self.request.GET.get("tab", "channels")
        return ctx


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
    page_title = "Nuevo Creador / Onboarding de Talento"
    page_subtitle = "Ficha de ingreso del creador a la compañía con opción de canal principal inmediato"
    list_url_name = "creators:creator_list"

    def get_success_url(self):
        return reverse("creators:creator_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        cleaned_data = form.cleaned_data.copy()

        # Extraer datos de canal inicial si se seleccionó en el formulario
        link_initial = cleaned_data.pop("link_initial_channel", False)
        initial_channel_data = None
        if link_initial and cleaned_data.get("initial_platform"):
            initial_channel_data = {
                "platform": cleaned_data.pop("initial_platform"),
                "platform_channel_id": cleaned_data.pop("initial_channel_id", "")
                or cleaned_data.get("handle", ""),
                "channel_url": cleaned_data.pop("initial_channel_url", ""),
                "followers_count": cleaned_data.pop("initial_followers_count", 0) or 0,
            }
        else:
            cleaned_data.pop("initial_platform", None)
            cleaned_data.pop("initial_channel_id", None)
            cleaned_data.pop("initial_channel_url", None)
            cleaned_data.pop("initial_followers_count", None)

        try:
            self.object = CreatorService.save_creator(
                initial_channel_data=initial_channel_data,
                **cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Creador '{self.object.display_name}' dado de alta exitosamente en el roster.",
        )
        return redirect(self.get_success_url())


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
    page_title = "Editar Creador"
    page_subtitle = "Actualización de identidad pública y configuración de talento"
    list_url_name = "creators:creator_list"

    def get_success_url(self):
        return reverse("creators:creator_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        try:
            self.object = CreatorService.save_creator(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Creador '{self.object.display_name}' actualizado exitosamente.",
        )
        return redirect(self.get_success_url())


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
    page_title = "Confirmar Baja de Creador"

    def form_valid(self, form):
        creator = self.get_object()
        name = creator.display_name
        CreatorService.delete_creator(instance=creator)
        messages.success(self.request, f"Creador '{name}' eliminado exitosamente.")
        return redirect(self.success_url)


class CreatorPersonalInfoUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = CreatorPersonalInfo
    permission_required = "creators.change_creator"
    form_class = CreatorPersonalInfoForm
    template_name = "creators/creator_personal_info_form.html"
    page_title = "Expediente Confidencial y Datos Bancarios (KYC)"
    page_subtitle = (
        "Información fiscal y cuenta receptora para liquidaciones de ingresos"
    )

    def get_object(self, queryset=None):
        creator_pk = self.kwargs.get("creator_pk")
        creator = get_object_or_404(
            CreatorSelector.get_visible_queryset(user=self.request.user),
            pk=creator_pk,
        )
        personal_info, _ = CreatorPersonalInfo.objects.get_or_create(creator=creator)
        return personal_info

    def get_success_url(self):
        return (
            reverse(
                "creators:creator_detail",
                kwargs={"pk": self.object.creator_id},
            )
            + "?tab=personal"
        )

    def form_valid(self, form):
        self.object = CreatorService.save_personal_info(
            creator=self.object.creator,
            **form.cleaned_data,
        )
        messages.success(
            self.request,
            "Datos personales, fiscales y bancarios guardados con éxito.",
        )
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["creator"] = self.object.creator
        ctx["cancel_url"] = reverse(
            "creators:creator_detail",
            kwargs={"pk": self.object.creator_id},
        )
        return ctx


class CreatorStatusChangeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "creators.change_creator"

    def post(self, request, pk):
        creator = get_object_or_404(
            CreatorSelector.get_visible_queryset(user=request.user),
            pk=pk,
        )
        form = CreatorStatusChangeForm(request.POST)
        if form.is_valid():
            try:
                CreatorService.change_status(
                    creator=creator,
                    new_status=form.cleaned_data["status"],
                    reason=form.cleaned_data.get("reason", ""),
                )
                status_label = creator.get_status_display()
                messages.success(
                    request,
                    f"Estado de {creator.display_name} modificado a '{status_label}'.",
                )
            except BusinessLogicError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Datos de cambio de estado inválidos.")
        return redirect("creators:creator_detail", pk=creator.pk)
