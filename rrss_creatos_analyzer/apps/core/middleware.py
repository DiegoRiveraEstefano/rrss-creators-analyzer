from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django_ratelimit.exceptions import Ratelimited

from .demo_baseline import is_baseline_user

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest
    from django.http import HttpResponse

PROTECTED_DEMO_ACCOUNT_PREFIXES: tuple[str, ...] = (
    "/accounts/password/",
    "/accounts/email/",
    "/accounts/2fa/",
    "/accounts/mfa/",
)

MUTATION_HTTP_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class RatelimitMiddleware:
    """Return HTTP 429 when django-ratelimit blocks a request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(
        self,
        request: HttpRequest,
        exception: Exception,
    ) -> HttpResponse | None:
        if isinstance(exception, Ratelimited):
            return render(request, "429.html", status=429)
        return None


class DemoProtectionMiddleware:
    """Protect shared demo accounts and destructive system operations in DEMO_MODE."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if (
            getattr(settings, "DEMO_MODE", False)
            and request.method in MUTATION_HTTP_METHODS
            and request.user.is_authenticated
        ):
            if is_baseline_user(request.user) and request.path.startswith(
                PROTECTED_DEMO_ACCOUNT_PREFIXES,
            ):
                raise PermissionDenied(
                    _(
                        "Shared demo accounts cannot modify passwords, "
                        "emails, or MFA settings.",
                    ),
                )
            if (
                not request.user.is_superuser
                and request.path.startswith("/backups/")
                and (
                    request.path.endswith("/create/")
                    or "/edit/" in request.path
                    or "/delete/" in request.path
                )
            ):
                raise PermissionDenied(
                    _("Database backup mutations are disabled in demo mode."),
                )
        return self.get_response(request)
