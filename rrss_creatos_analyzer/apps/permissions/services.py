import logging

from django.contrib.auth.models import Group
from django.db import transaction

from .models import RoleGroupProfile

logger = logging.getLogger(__name__)


class RoleGroupProfileService:
    @classmethod
    @transaction.atomic
    def save_role_profile(  # noqa: PLR0913
        cls,
        *,
        instance: RoleGroupProfile | None = None,
        group_name: str,
        permissions=None,
        description: str = "",
        badge_color: str = "primary",
        is_system_role: bool = False,
    ) -> RoleGroupProfile:
        if instance:
            group = instance.group
            group.name = group_name
            group.save()
            profile = instance
        else:
            group, _ = Group.objects.get_or_create(name=group_name)
            profile, _ = RoleGroupProfile.objects.get_or_create(group=group)

        profile.description = description
        profile.badge_color = badge_color
        profile.is_system_role = is_system_role
        profile.save()

        if permissions is not None:
            group.permissions.set(permissions)

        logger.info(
            "role_group_profile_saved",
            extra={"role_profile_id": profile.id, "group_name": group.name},
        )
        return profile

    @classmethod
    @transaction.atomic
    def delete_role_profile(cls, *, instance: RoleGroupProfile) -> None:
        pid = instance.id
        instance.group.delete()
        logger.info("role_group_profile_deleted", extra={"role_profile_id": pid})
