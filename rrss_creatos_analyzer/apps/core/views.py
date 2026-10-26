from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .exceptions import BusinessLogicError
from .filters import CompanySettingsFilter
from .forms import CompanySettingsForm
from .models import CompanySettings
from .selectors import CompanySettingsSelector
from .services import CompanySettingsService
from .tables import CompanySettingsTable


class HomeDashboardView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx.update(CompanySettingsSelector.get_dashboard_summary())
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"


class CompanySettingsListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleTableMixin,
    FilterView,
):
    model = CompanySettings
    permission_required = "core.view_companysettings"
    table_class = CompanySettingsTable
    filterset_class = CompanySettingsFilter
    template_name = "core/companysettings_list.html"
    paginate_by = 20

    def get_queryset(self):
        return CompanySettingsSelector.get_queryset()


class CompanySettingsDetailView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):
    model = CompanySettings
    permission_required = "core.view_companysettings"
    template_name = "core/companysettings_detail.html"
    context_object_name = "settings_obj"


class CompanySettingsCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = CompanySettings
    permission_required = "core.add_companysettings"
    form_class = CompanySettingsForm
    template_name = "core/companysettings_form.html"
    success_url = reverse_lazy("core:settings_list")

    def form_valid(self, form):
        try:
            self.object = CompanySettingsService.save_settings(**form.cleaned_data)
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Configuración de compañía creada exitosamente.")
        return redirect(self.success_url)


class CompanySettingsUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = CompanySettings
    permission_required = "core.change_companysettings"
    form_class = CompanySettingsForm
    template_name = "core/companysettings_form.html"
    success_url = reverse_lazy("core:settings_list")

    def form_valid(self, form):
        try:
            self.object = CompanySettingsService.save_settings(
                instance=self.get_object(),
                **form.cleaned_data,
            )
        except BusinessLogicError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(
            self.request,
            "Configuración de compañía actualizada exitosamente.",
        )
        return redirect(self.success_url)


class CompanySettingsDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    model = CompanySettings
    permission_required = "core.delete_companysettings"
    template_name = "core/companysettings_confirm_delete.html"
    success_url = reverse_lazy("core:settings_list")

    def form_valid(self, form):
        CompanySettingsService.delete_settings(instance=self.get_object())
        messages.success(self.request, "Configuración eliminada.")
        return redirect(self.success_url)
