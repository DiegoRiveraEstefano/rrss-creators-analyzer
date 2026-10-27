from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Creator


@auditlog.register()
class CreatorScheduleComplianceSummary(BaseModel):
    """Consolidado mensual del cumplimiento contractual de pauta horaria."""

    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="schedule_compliance_summaries",
        verbose_name=_("Creador"),
    )
    year = models.PositiveIntegerField(_("Año"), db_index=True)
    month = models.PositiveSmallIntegerField(_("Mes"), db_index=True)

    stipulated_days_count = models.PositiveIntegerField(
        _("Días Estipulados Brutos"),
        default=0,
    )
    justified_days_count = models.PositiveIntegerField(
        _("Días Justificados / Licencias"),
        default=0,
    )
    completed_days_count = models.PositiveIntegerField(
        _("Días Cumplidos"),
        default=0,
    )
    late_days_count = models.PositiveIntegerField(
        _("Días con Retraso"),
        default=0,
    )
    partial_days_count = models.PositiveIntegerField(
        _("Días Parciales"),
        default=0,
    )
    missed_days_count = models.PositiveIntegerField(
        _("Días Incumplidos (Faltas)"),
        default=0,
    )

    stipulated_hours = models.DecimalField(
        _("Horas Estipuladas Brutas"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    justified_hours = models.DecimalField(
        _("Horas Justificadas"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    actual_hours = models.DecimalField(
        _("Horas Efectivas Transmitidas"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    days_compliance_rate_pct = models.DecimalField(
        _("Cumplimiento en Días (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    hours_compliance_rate_pct = models.DecimalField(
        _("Cumplimiento en Horas (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    punctuality_rate_pct = models.DecimalField(
        _("Tasa de Puntualidad (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    is_compliant = models.BooleanField(
        _("Cumplió Meta Mensual"),
        default=False,
        db_index=True,
    )
    audit_notes = models.TextField(_("Notas de Auditoría"), blank=True)
    calculated_at = models.DateTimeField(
        _("Fecha/Hora de Cálculo"),
        auto_now=True,
    )

    history = HistoricalRecords()

    class Meta:
        app_label = "schedules"
        verbose_name = _("Resumen Mensual de Cumplimiento")
        verbose_name_plural = _("Resúmenes Mensuales de Cumplimiento")
        ordering = ["-year", "-month", "creator"]
        constraints = [
            models.UniqueConstraint(
                fields=["creator", "year", "month"],
                name="unique_creator_schedule_compliance_per_month",
            ),
            models.CheckConstraint(
                condition=Q(month__gte=1) & Q(month__lte=12),
                name="chk_summary_valid_month",
            ),
            models.CheckConstraint(
                condition=Q(year__gte=2020) & Q(year__lte=2100),
                name="chk_summary_valid_year",
            ),
        ]

    def __str__(self) -> str:
        period = f"{self.month:02d}/{self.year}"
        pct = self.days_compliance_rate_pct
        return f"{self.creator.display_name} - {period} ({pct}%)"

    def get_absolute_url(self) -> str:
        return reverse("schedules:compliance_detail", kwargs={"pk": self.pk})
