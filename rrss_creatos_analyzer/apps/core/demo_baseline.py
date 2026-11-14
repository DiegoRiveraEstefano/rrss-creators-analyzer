from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from django.contrib.contenttypes.models import ContentType

from .models import DemoBaselineRecord

if TYPE_CHECKING:
    from django.db import models

BASELINE_USERNAMES: tuple[str, ...] = (
    "demo_admin",
    "demo_manager",
    "demo_analyst",
    "demo_finance",
    "demo_creator",
)

DEMO_SIGNUP_ROLES: tuple[str, ...] = (
    "Manager",
    "Analyst",
    "Finance",
    "Creator",
)


def mark_baseline(instance: models.Model) -> DemoBaselineRecord:
    """Register an instance in DemoBaselineRecord so retention cleanup preserves it."""
    content_type = ContentType.objects.get_for_model(
        instance,
        for_concrete_model=False,
    )
    record, _ = DemoBaselineRecord.objects.get_or_create(
        content_type=content_type,
        object_id=str(instance.pk),
    )
    return record


def is_baseline_object(instance: models.Model) -> bool:
    """Return True if instance is registered as a protected demo baseline record."""
    if instance.pk is None:
        return False
    content_type = ContentType.objects.get_for_model(
        instance,
        for_concrete_model=False,
    )
    return DemoBaselineRecord.objects.filter(
        content_type=content_type,
        object_id=str(instance.pk),
    ).exists()


def is_baseline_user(user: Any) -> bool:
    """Return True if user is a shared baseline demo account."""
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "username", "") in BASELINE_USERNAMES:
        return True
    return is_baseline_object(user)


def get_baseline_pks(model: type[models.Model]) -> list[Any]:
    """Return primary keys registered in DemoBaselineRecord for the given model."""
    content_type = ContentType.objects.get_for_model(
        model,
        for_concrete_model=False,
    )
    raw_ids = DemoBaselineRecord.objects.filter(
        content_type=content_type,
    ).values_list("object_id", flat=True)
    pk_field = model._meta.pk  # noqa: SLF001
    if pk_field is None:
        return []
    return [pk_field.to_python(raw_id) for raw_id in raw_ids]
