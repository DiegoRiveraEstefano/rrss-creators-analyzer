from auditlog.registry import auditlog
from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.models import BaseModel


@auditlog.register()
class RoleGroupProfile(BaseModel):
    """Metadata profile extending native Django auth.Group."""

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="role_profile",
        verbose_name=_("Grupo de Django"),
    )
    description = models.TextField(_("Descripción del Rol"), blank=True)
    badge_color = models.CharField(
        _("Color de Insignia (Bootstrap)"),
        max_length=30,
        default="primary",
    )
    is_system_role = models.BooleanField(_("Es Rol Base del Sistema"), default=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Perfil de Grupo / Rol")
        verbose_name_plural = _("Perfiles de Grupos / Roles")
        ordering = ["group__name"]

    def __str__(self) -> str:
        return self.group.name

    def get_absolute_url(self) -> str:
        return reverse("permissions:role_detail", kwargs={"pk": self.pk})
