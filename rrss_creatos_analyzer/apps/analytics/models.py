from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.models import BaseModel


class AnalyticsSnapshot(BaseModel):
    cache_key = models.CharField(
        _("Clave de DiskCache"),
        max_length=150,
        unique=True,
        db_index=True,
    )
    report_type = models.CharField(
        _("Tipo de Reporte"),
        max_length=60,
        default="creator_performance_summary",
        db_index=True,
    )
    period_label = models.CharField(
        _("Periodo (YYYY-MM / Global)"),
        max_length=30,
        default="global",
    )
    payload = models.JSONField(_("Datos Consolidados (JSON)"), default=dict, blank=True)
    records_count = models.PositiveIntegerField(_("Registros Procesados"), default=0)
    expires_at = models.DateTimeField(_("Expira en Caché"), null=True, blank=True)

    class Meta:
        verbose_name = _("Snapshot Analítico (DiskCache)")
        verbose_name_plural = _("Snapshots Analíticos (DiskCache)")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.report_type} [{self.cache_key}]"

    def get_absolute_url(self) -> str:
        return reverse("analytics:snapshot_detail", kwargs={"pk": self.pk})
