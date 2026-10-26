from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.choices import AlertSeverity
from rrss_creatos_analyzer.apps.core.choices import AlertStatus
from rrss_creatos_analyzer.apps.core.choices import AlertType
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.videos.models import VideoPublication


class ChannelAlert(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name=_("Creador"),
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
        verbose_name=_("Canal"),
    )
    related_session = models.ForeignKey(
        StreamingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
        verbose_name=_("Sesión Relacionada"),
    )
    related_publication = models.ForeignKey(
        VideoPublication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
        verbose_name=_("Publicación Relacionada"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_alerts",
        verbose_name=_("Asignado a"),
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
        verbose_name=_("Resuelto por"),
    )

    alert_type = models.CharField(
        _("Tipo de Alerta"),
        max_length=40,
        choices=AlertType.choices,
        default=AlertType.TOS_VIOLATION,
    )
    severity = models.CharField(
        _("Severidad"),
        max_length=20,
        choices=AlertSeverity.choices,
        default=AlertSeverity.WARNING,
        db_index=True,
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE,
        db_index=True,
    )

    strike_points = models.PositiveIntegerField(_("Puntos de Strike (0-3)"), default=0)
    strike_expires_at = models.DateTimeField(
        _("Expiración del Strike"),
        null=True,
        blank=True,
    )
    account_suspension_days = models.PositiveIntegerField(
        _("Días de Suspensión"),
        default=0,
    )

    title = models.CharField(_("Título de la Alerta"), max_length=255)
    description = models.TextField(_("Descripción Detallada"), blank=True)
    evidence_url = models.URLField(_("URL de Evidencia"), max_length=500, blank=True)
    occurred_at = models.DateTimeField(_("Ocurrido el"), db_index=True)
    resolved_at = models.DateTimeField(_("Resuelto el"), null=True, blank=True)
    resolution_notes = models.TextField(
        _("Notas de Resolución / Apelación"),
        blank=True,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Alerta de Canal")
        verbose_name_plural = _("Alertas de Canal")
        ordering = ["-occurred_at"]
        permissions = [
            ("view_all_alerts", _("Puede ver las alertas de todos los canales")),
            ("resolve_channel_alert", _("Puede resolver o apelar alertas y strikes")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(strike_points__gte=0) & Q(account_suspension_days__gte=0),
                name="chk_alert_strikes_non_negative",
            ),
        ]

    def __str__(self) -> str:
        sev = self.get_severity_display()
        return f"[{sev}] {self.title} - {self.creator.display_name}"

    def get_absolute_url(self) -> str:
        return reverse("alerts:alert_detail", kwargs={"pk": self.pk})
