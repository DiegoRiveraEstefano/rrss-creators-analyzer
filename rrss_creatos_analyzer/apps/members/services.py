import logging

from django.db import transaction

from .models import CreatorTeamAssignment
from .models import MemberInvitation

logger = logging.getLogger(__name__)


class MemberInvitationService:
    @classmethod
    @transaction.atomic
    def save_invitation(
        cls,
        *,
        instance: MemberInvitation | None = None,
        **data,
    ) -> MemberInvitation:
        inv = instance or MemberInvitation()
        for field, value in data.items():
            setattr(inv, field, value)
        inv.save()
        logger.info(
            "member_invitation_saved",
            extra={"invitation_id": inv.id, "email": inv.email},
        )
        return inv

    @classmethod
    @transaction.atomic
    def delete_invitation(cls, *, instance: MemberInvitation) -> None:
        iid = instance.id
        instance.delete()
        logger.info("member_invitation_deleted", extra={"invitation_id": iid})


class CreatorTeamAssignmentService:
    @classmethod
    @transaction.atomic
    def save_assignment(
        cls,
        *,
        instance: CreatorTeamAssignment | None = None,
        **data,
    ) -> CreatorTeamAssignment:
        assign = instance or CreatorTeamAssignment()
        for field, value in data.items():
            setattr(assign, field, value)
        assign.save()
        logger.info(
            "team_assignment_saved",
            extra={"assignment_id": assign.id, "creator_id": assign.creator_id},
        )
        return assign

    @classmethod
    @transaction.atomic
    def delete_assignment(cls, *, instance: CreatorTeamAssignment) -> None:
        aid = instance.id
        instance.delete()
        logger.info("team_assignment_deleted", extra={"assignment_id": aid})
