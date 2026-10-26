from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.models import BaseModel


class AuditEvent(BaseModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
        verbose_name=_("Actor / Usuario"),
    )
    event_action = models.CharField(_("Acción"), max_length=100, db_index=True)
    target_model = models.CharField(_("Modelo Afectado"), max_length=100)
    target_object_id = models.CharField(_("ID Objeto"), max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(_("Dirección IP"), null=True, blank=True)
    summary = models.CharField(_("Resumen"), max_length=255)
    changes_payload = models.JSONField(
        _("Detalle de Cambios"),
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = _("Evento de Auditoría")
        verbose_name_plural = _("Eventos de Auditoría")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        ts = f"{self.created_at:%Y-%m-%d %H:%M}"
        return f"{self.event_action} on {self.target_model} ({ts})"

    def get_absolute_url(self) -> str:
        return reverse("audit:audit_detail", kwargs={"pk": self.pk})
