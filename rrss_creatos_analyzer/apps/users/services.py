from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.text import slugify

from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorTier
from rrss_creatos_analyzer.apps.core.demo_baseline import DEMO_SIGNUP_ROLES
from rrss_creatos_analyzer.apps.core.demo_services import DemoSeedService
from rrss_creatos_analyzer.apps.creators.models import Creator

if TYPE_CHECKING:
    from .models import User

logger = logging.getLogger(__name__)


class UserService:
    @classmethod
    @transaction.atomic
    def update_user_profile(cls, *, user: User, name: str) -> User:
        user.name = name
        user.save(update_fields=["name"])
        logger.info("user_profile_updated", extra={"user_id": user.id})
        return user

    @classmethod
    @transaction.atomic
    def assign_default_role(
        cls,
        *,
        user: User,
        role_name: str | None = None,
    ) -> Group:
        """Assign an RBAC Group on signup and provision a Creator profile if needed."""
        default_role = getattr(settings, "DEMO_DEFAULT_SIGNUP_GROUP", "Manager")
        target_role = (
            role_name
            if getattr(settings, "DEMO_MODE", False) and role_name in DEMO_SIGNUP_ROLES
            else default_role
        )
        group = Group.objects.filter(name=target_role).first()
        if group is None:
            groups = DemoSeedService.seed_roles()
            group = (
                groups.get(target_role)
                or Group.objects.get_or_create(
                    name=target_role,
                )[0]
            )

        user.groups.add(group)

        if group.name == "Creator" and not Creator.objects.filter(user=user).exists():
            base_handle = slugify(user.username) or f"creator-{user.pk}"
            handle = base_handle
            if Creator.objects.filter(handle=handle).exists():
                handle = f"{base_handle}-{user.pk}"
            Creator.objects.create(
                user=user,
                display_name=user.name or user.username,
                handle=handle,
                slug=handle,
                tier=CreatorTier.ROOKIE,
                status=CreatorStatus.ACTIVE,
            )

        logger.info(
            "user_default_role_assigned",
            extra={"user_id": user.id, "role": group.name},
        )
        return group
