import django_tables2 as tables

from .models import CreatorTeamAssignment
from .models import MemberInvitation


class MemberInvitationTable(tables.Table):
    email = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="members/includes/invitation_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = MemberInvitation
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "email",
            "full_name",
            "target_group",
            "status",
            "invited_by",
            "expires_at",
            "created_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}


class CreatorTeamAssignmentTable(tables.Table):
    creator = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="members/includes/assignment_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = CreatorTeamAssignment
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "creator",
            "user",
            "group",
            "responsibility",
            "is_primary",
            "created_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
