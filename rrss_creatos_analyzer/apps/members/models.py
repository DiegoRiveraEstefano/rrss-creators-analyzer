import secrets

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.choices import TeamResponsibility
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Creator


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


class MemberInvitation(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pendiente")
        ACCEPTED = "accepted", _("Aceptada")
        EXPIRED = "expired", _("Expirada")
        REVOKED = "revoked", _("Revocada")

    email = models.EmailField(_("Email del Invitado"))
    full_name = models.CharField(_("Nombre del Invitado"), max_length=150, blank=True)
    token = models.CharField(
        _("Token"),
        max_length=64,
        unique=True,
        default=generate_invite_token,
    )
    target_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_invitations",
        verbose_name=_("Grupo de Permisos Asignado"),
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invitations",
        verbose_name=_("Invitado Por"),
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    expires_at = models.DateTimeField(_("Expira el"))
    accepted_at = models.DateTimeField(_("Aceptada el"), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Invitación de Miembro")
        verbose_name_plural = _("Invitaciones de Miembros")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.email} ({self.get_status_display()})"

    def get_absolute_url(self) -> str:
        return reverse("members:invitation_detail", kwargs={"pk": self.pk})


class CreatorTeamAssignment(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="team_assignments",
        verbose_name=_("Creador"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creator_assignments",
        verbose_name=_("Miembro del Equipo"),
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_assignments",
        verbose_name=_("Grupo de Rol"),
    )
    responsibility = models.CharField(
        _("Responsabilidad Operativa"),
        max_length=40,
        choices=TeamResponsibility.choices,
        default=TeamResponsibility.TALENT_MANAGER,
    )
    is_primary = models.BooleanField(_("Responsable Principal"), default=False)

    class Meta:
        verbose_name = _("Asignación de Equipo")
        verbose_name_plural = _("Asignaciones de Equipo")
        ordering = ["creator", "-is_primary"]
        constraints = [
            models.UniqueConstraint(
                fields=["creator", "user", "responsibility"],
                name="uq_creator_user_responsibility",
            ),
        ]

    def __str__(self) -> str:
        resp = self.get_responsibility_display()
        return f"{self.user} -> {self.creator.display_name} ({resp})"

    def get_absolute_url(self) -> str:
        return reverse("members:assignment_detail", kwargs={"pk": self.pk})
