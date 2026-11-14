from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from django.conf import settings

if TYPE_CHECKING:
    from django.http import HttpRequest

DEMO_QUICK_ROLES: tuple[dict[str, str], ...] = (
    {
        "role": "Manager",
        "username": "demo_manager",
        "label": "Manager",
        "badge_class": "primary",
        "summary": "Roster, streams, videos, schedules, and analytics.",
    },
    {
        "role": "Analyst",
        "username": "demo_analyst",
        "label": "Analyst",
        "badge_class": "info",
        "summary": "Analytics, performance reports, and bulk imports.",
    },
    {
        "role": "Finance",
        "username": "demo_finance",
        "label": "Finance",
        "badge_class": "success",
        "summary": "Contracts, sponsorships, and creator payouts.",
    },
    {
        "role": "Creator",
        "username": "demo_creator",
        "label": "Creator",
        "badge_class": "warning",
        "summary": "Personal profile, streams, videos, and payouts.",
    },
)


def demo_context(request: HttpRequest) -> dict[str, Any]:
    """Expose demo mode, retention window, and CAPTCHA flags to templates."""
    demo_mode = bool(getattr(settings, "DEMO_MODE", False))
    return {
        "DEMO_MODE": demo_mode,
        "DEMO_DATA_RETENTION_DAYS": int(
            getattr(settings, "DEMO_DATA_RETENTION_DAYS", 7),
        ),
        "CAPTCHA_ENABLED": bool(getattr(settings, "CAPTCHA_ENABLED", False)),
        "DEMO_QUICK_ROLES": DEMO_QUICK_ROLES if demo_mode else (),
    }
