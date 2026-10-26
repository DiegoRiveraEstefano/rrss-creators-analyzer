from typing import TYPE_CHECKING

from .models import CreatorTeamAssignment
from .models import MemberInvitation

if TYPE_CHECKING:
    from django.db.models import QuerySet


class MemberInvitationSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[MemberInvitation]:
        return MemberInvitation.objects.select_related("target_group", "invited_by")


class CreatorTeamAssignmentSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[CreatorTeamAssignment]:
        return CreatorTeamAssignment.objects.select_related("creator", "user", "group")
