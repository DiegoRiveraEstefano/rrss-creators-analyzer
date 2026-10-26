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

from .filters import CampaignDeliverableFilter
from .filters import SponsorCampaignFilter
from .forms import CampaignDeliverableForm
from .forms import SponsorCampaignForm
from .models import CampaignDeliverable
from .models import SponsorCampaign
from .selectors import CampaignDeliverableSelector
from .selectors import SponsorCampaignSelector
from .services import CampaignDeliverableService
from .services import SponsorCampaignService
from .tables import CampaignDeliverableTable
from .tables import SponsorCampaignTable


class SponsorCampaignListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = SponsorCampaign
    permission_required = "campaigns.view_sponsorcampaign"
    table_class = SponsorCampaignTable
    filterset_class = SponsorCampaignFilter
    template_name = "campaigns/campaign_list.html"
    paginate_by = 25
    page_title = "Campañas Comerciales y Patrocinios"
    page_subtitle = "Gestión de marcas, presupuestos, comisiones y pool de creadores"
    create_url_name = "campaigns:campaign_create"

    def get_queryset(self):
        return SponsorCampaignSelector.get_queryset()


class SponsorCampaignDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = SponsorCampaign
    permission_required = "campaigns.view_sponsorcampaign"
    template_name = "campaigns/campaign_detail.html"
    page_title = "Detalle de Campaña"
    list_url_name = "campaigns:campaign_list"
    update_url_name = "campaigns:campaign_update"
    delete_url_name = "campaigns:campaign_delete"


class SponsorCampaignCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = SponsorCampaign
    permission_required = "campaigns.add_sponsorcampaign"
    form_class = SponsorCampaignForm
    template_name = "campaigns/campaign_form.html"
    success_url = reverse_lazy("campaigns:campaign_list")
    page_title = "Nueva Campaña de Patrocinio"
    list_url_name = "campaigns:campaign_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = SponsorCampaignService.save_campaign(tags=tags, **data)
        messages.success(self.request, "Campaña creada exitosamente.")
        return redirect(self.success_url)


class SponsorCampaignUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = SponsorCampaign
    permission_required = "campaigns.change_sponsorcampaign"
    form_class = SponsorCampaignForm
    template_name = "campaigns/campaign_form.html"
    success_url = reverse_lazy("campaigns:campaign_list")
    page_title = "Editar Campaña de Patrocinio"
    list_url_name = "campaigns:campaign_list"

    def form_valid(self, form):
        data = form.cleaned_data.copy()
        tags = data.pop("tags", None)
        self.object = SponsorCampaignService.save_campaign(
            instance=self.get_object(),
            tags=tags,
            **data,
        )
        messages.success(self.request, "Campaña actualizada exitosamente.")
        return redirect(self.success_url)


class SponsorCampaignDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = SponsorCampaign
    permission_required = "campaigns.delete_sponsorcampaign"
    template_name = "campaigns/campaign_confirm_delete.html"
    success_url = reverse_lazy("campaigns:campaign_list")
    list_url_name = "campaigns:campaign_list"

    def form_valid(self, form):
        SponsorCampaignService.delete_campaign(instance=self.get_object())
        messages.success(self.request, "Campaña eliminada.")
        return redirect(self.success_url)


# ==== DELIVERABLE CRUD ====
class CampaignDeliverableListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = CampaignDeliverable
    permission_required = "campaigns.view_campaigndeliverable"
    table_class = CampaignDeliverableTable
    filterset_class = CampaignDeliverableFilter
    template_name = "campaigns/deliverable_list.html"
    paginate_by = 25
    page_title = "Entregables de Campaña"
    create_url_name = "campaigns:deliverable_create"

    def get_queryset(self):
        return CampaignDeliverableSelector.get_visible_queryset(user=self.request.user)


class CampaignDeliverableDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = CampaignDeliverable
    permission_required = "campaigns.view_campaigndeliverable"
    template_name = "campaigns/deliverable_detail.html"
    page_title = "Detalle de Entregable"
    list_url_name = "campaigns:deliverable_list"
    update_url_name = "campaigns:deliverable_update"
    delete_url_name = "campaigns:deliverable_delete"

    def get_queryset(self):
        return CampaignDeliverableSelector.get_visible_queryset(user=self.request.user)


class CampaignDeliverableCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = CampaignDeliverable
    permission_required = "campaigns.add_campaigndeliverable"
    form_class = CampaignDeliverableForm
    template_name = "campaigns/deliverable_form.html"
    success_url = reverse_lazy("campaigns:deliverable_list")
    page_title = "Nuevo Entregable de Campaña"
    list_url_name = "campaigns:deliverable_list"

    def form_valid(self, form):
        self.object = CampaignDeliverableService.save_deliverable(**form.cleaned_data)
        messages.success(self.request, "Entregable creado exitosamente.")
        return redirect(self.success_url)


class CampaignDeliverableUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = CampaignDeliverable
    permission_required = "campaigns.change_campaigndeliverable"
    form_class = CampaignDeliverableForm
    template_name = "campaigns/deliverable_form.html"
    success_url = reverse_lazy("campaigns:deliverable_list")
    page_title = "Editar Entregable de Campaña"
    list_url_name = "campaigns:deliverable_list"

    def form_valid(self, form):
        self.object = CampaignDeliverableService.save_deliverable(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Entregable actualizado exitosamente.")
        return redirect(self.success_url)


class CampaignDeliverableDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = CampaignDeliverable
    permission_required = "campaigns.delete_campaigndeliverable"
    template_name = "campaigns/deliverable_confirm_delete.html"
    success_url = reverse_lazy("campaigns:deliverable_list")
    list_url_name = "campaigns:deliverable_list"

    def form_valid(self, form):
        CampaignDeliverableService.delete_deliverable(instance=self.get_object())
        messages.success(self.request, "Entregable eliminado.")
        return redirect(self.success_url)
