from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_ratelimit.decorators import ratelimit
from django_tables2 import SingleTableMixin

from .demo_services import DemoSeedService
from .exceptions import BusinessLogicError
from .filters import CompanySettingsFilter
from .forms import CompanySettingsForm
from .models import CompanySettings
from .selectors import CompanySettingsSelector
from .services import CompanySettingsService
from .tables import CompanySettingsTable

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import HttpResponse

User = get_user_model()

QUICK_DEMO_ROLE_MAP: dict[str, str] = {
    "Manager": "demo_manager",
    "Analyst": "demo_analyst",
    "Finance": "demo_finance",
    "Creator": "demo_creator",
}


class HomeDashboardView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx.update(CompanySettingsSelector.get_dashboard_summary())
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"


@method_decorator(
    ratelimit(key="ip", rate="15/m", method="POST", block=True),
    name="dispatch",
)
class DemoQuickLoginView(View):
    """One-click role login endpoint active only when DEMO_MODE=True."""

    def get(self, request: HttpRequest) -> HttpResponse:
        if not getattr(settings, "DEMO_MODE", False):
            return HttpResponseNotFound()
        return redirect("account_login")

    def post(self, request: HttpRequest) -> HttpResponse:
        if not getattr(settings, "DEMO_MODE", False):
            return HttpResponseNotFound()

        role = request.POST.get("role", "").strip()
        username = QUICK_DEMO_ROLE_MAP.get(role)
        if not username:
            messages.error(request, _("Invalid demo role selected."))
            return redirect("account_login")

        user = User.objects.filter(username=username, is_active=True).first()
        if user is None:
            DemoSeedService.seed_all()
            user = User.objects.filter(username=username, is_active=True).first()

        if user is None:
            messages.error(request, _("Demo account is currently unavailable."))
            return redirect("account_login")

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        messages.success(
            request,
            _("Signed in as demo %(role)s (%(username)s).")
            % {"role": role, "username": user.username},
        )
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect(reverse("home"))


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
