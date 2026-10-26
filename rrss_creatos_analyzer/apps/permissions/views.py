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

from .filters import RoleGroupProfileFilter
from .forms import RoleGroupProfileForm
from .models import RoleGroupProfile
from .selectors import RoleGroupProfileSelector
from .services import RoleGroupProfileService
from .tables import RoleGroupProfileTable


class RoleGroupProfileListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    SingleTableMixin,
    FilterView,
):
    model = RoleGroupProfile
    permission_required = "permissions.view_rolegroupprofile"
    table_class = RoleGroupProfileTable
    filterset_class = RoleGroupProfileFilter
    template_name = "permissions/role_list.html"
    paginate_by = 25
    page_title = "Grupos y Permisos de Django"
    page_subtitle = (
        "Administración de roles de negocio sobre django.contrib.auth.models.Group"
    )
    create_url_name = "permissions:role_create"

    def get_queryset(self):
        return RoleGroupProfileSelector.get_queryset()


class RoleGroupProfileDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DetailView,
):
    model = RoleGroupProfile
    permission_required = "permissions.view_rolegroupprofile"
    template_name = "permissions/role_detail.html"
    page_title = "Detalle de Grupo de Permisos"
    list_url_name = "permissions:role_list"
    update_url_name = "permissions:role_update"
    delete_url_name = "permissions:role_delete"


class RoleGroupProfileCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    CreateView,
):
    model = RoleGroupProfile
    permission_required = "permissions.add_rolegroupprofile"
    form_class = RoleGroupProfileForm
    template_name = "permissions/role_form.html"
    success_url = reverse_lazy("permissions:role_list")
    page_title = "Nuevo Grupo de Permisos"
    list_url_name = "permissions:role_list"

    def form_valid(self, form):
        self.object = RoleGroupProfileService.save_role_profile(**form.cleaned_data)
        messages.success(self.request, "Grupo y permisos creados exitosamente.")
        return redirect(self.success_url)


class RoleGroupProfileUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    UpdateView,
):
    model = RoleGroupProfile
    permission_required = "permissions.change_rolegroupprofile"
    form_class = RoleGroupProfileForm
    template_name = "permissions/role_form.html"
    success_url = reverse_lazy("permissions:role_list")
    page_title = "Editar Grupo de Permisos"
    list_url_name = "permissions:role_list"

    def form_valid(self, form):
        self.object = RoleGroupProfileService.save_role_profile(
            instance=self.get_object(),
            **form.cleaned_data,
        )
        messages.success(self.request, "Grupo y permisos actualizados exitosamente.")
        return redirect(self.success_url)


class RoleGroupProfileDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CrudContextMixin,
    DeleteView,
):
    model = RoleGroupProfile
    permission_required = "permissions.delete_rolegroupprofile"
    template_name = "permissions/role_confirm_delete.html"
    success_url = reverse_lazy("permissions:role_list")
    list_url_name = "permissions:role_list"

    def form_valid(self, form):
        RoleGroupProfileService.delete_role_profile(instance=self.get_object())
        messages.success(self.request, "Grupo eliminado.")
        return redirect(self.success_url)
