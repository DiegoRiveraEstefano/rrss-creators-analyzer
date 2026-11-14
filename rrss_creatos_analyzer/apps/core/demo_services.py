from __future__ import annotations

import logging
import secrets
from decimal import Decimal
from typing import Any
from typing import cast

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.db import transaction

from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.permissions.models import RoleGroupProfile

from .demo_baseline import mark_baseline
from .demo_roles import DEMO_USERS_SPEC
from .demo_roles import LOCAL_APP_LABELS
from .demo_roles import ROLE_DEFINITIONS
from .demo_seed_business import seed_editors_and_business
from .demo_seed_ops import seed_streams_and_videos
from .demo_seed_roster import seed_contracts_and_schedules
from .demo_seed_roster import seed_creators_and_channels
from .models import CompanySettings
from .models import DemoBaselineRecord

logger = logging.getLogger(__name__)
User = get_user_model()


class DemoSeedService:
    """Idempotent service provisioning RBAC roles, demo accounts, and datasets."""

    @classmethod
    def is_seeded(cls) -> bool:
        """Return True when baseline demo users and creators already exist."""
        return (
            User.objects.filter(username="demo_manager").exists()
            and Creator.objects.exists()
            and DemoBaselineRecord.objects.exists()
        )

    @classmethod
    @transaction.atomic
    def seed_roles(cls) -> dict[str, Group]:
        """Create or synchronize the 5 standard RBAC Groups and RoleGroupProfiles."""
        groups: dict[str, Group] = {}
        all_local_perms = list(
            Permission.objects.filter(content_type__app_label__in=LOCAL_APP_LABELS),
        )
        for role_name, spec in ROLE_DEFINITIONS.items():
            group, _ = Group.objects.get_or_create(name=role_name)
            if spec.get("all_local_perms"):
                perms = all_local_perms
            else:
                perms = []
                for app_label, codenames in spec["perms"].items():
                    perms.extend(
                        Permission.objects.filter(
                            content_type__app_label=app_label,
                            codename__in=codenames,
                        ),
                    )
            group.permissions.set(perms)
            profile, _ = RoleGroupProfile.objects.update_or_create(
                group=group,
                defaults={
                    "description": spec["description"],
                    "badge_color": spec["badge_color"],
                    "is_system_role": True,
                },
            )
            mark_baseline(group)
            mark_baseline(profile)
            groups[role_name] = group
        return groups

    @classmethod
    @transaction.atomic
    def seed_demo_users(cls, groups: dict[str, Group]) -> dict[str, Any]:
        """Provision non-superuser baseline demo accounts linked to RBAC groups."""
        users: dict[str, Any] = {}
        for spec in DEMO_USERS_SPEC:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "name": spec["name"],
                    "is_active": True,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            if created or not user.has_usable_password():
                user.set_password(secrets.token_urlsafe(24))
                user.save(update_fields=["password"])
            user.groups.set([groups[spec["role"]]])
            email_obj, _ = EmailAddress.objects.update_or_create(
                user=user,
                email=spec["email"],
                defaults={"verified": True, "primary": True},
            )
            mark_baseline(user)
            mark_baseline(email_obj)
            users[spec["username"]] = user
        return users

    @classmethod
    @transaction.atomic
    def _reset_baseline(cls) -> None:
        """Delete existing baseline objects before rebuilding a clean demo snapshot."""
        for record in DemoBaselineRecord.objects.select_related("content_type"):
            model = record.content_type.model_class()
            if model is None or model in (Group, RoleGroupProfile):
                continue
            pk_field = model._meta.pk  # noqa: SLF001
            if pk_field is not None:
                cast("Any", model).objects.filter(
                    pk=pk_field.to_python(record.object_id),
                ).delete()
        DemoBaselineRecord.objects.all().delete()

    @classmethod
    @transaction.atomic
    def seed_all(cls, *, reset: bool = False) -> dict[str, int]:
        """Populate baseline roles, demo users, settings, and domain datasets."""
        if reset:
            cls._reset_baseline()

        groups = cls.seed_roles()
        users = cls.seed_demo_users(groups)

        company_settings, _ = CompanySettings.objects.get_or_create(
            company_name="Horizon Creator Agency (Demo)",
            defaults={
                "legal_name": "Horizon Talent Operations LLC",
                "default_currency": "USD",
                "default_timezone": "UTC",
                "default_agency_split_pct": Decimal("20.00"),
                "default_creator_split_pct": Decimal("80.00"),
            },
        )
        mark_baseline(company_settings)

        roster = seed_creators_and_channels(users=users, groups=groups)
        contract_nova, pattern = seed_contracts_and_schedules(
            users=users,
            roster=roster,
        )
        media = seed_streams_and_videos(
            users=users,
            roster=roster,
            pattern=pattern,
        )
        summary = seed_editors_and_business(
            users=users,
            roster=roster,
            media=media,
            contract_nova=contract_nova,
        )
        summary["roles"] = len(groups)
        summary["users"] = len(users)
        transaction.on_commit(cache.clear)
        logger.info("demo_seed_completed", extra={"summary": summary, "reset": reset})
        return summary
