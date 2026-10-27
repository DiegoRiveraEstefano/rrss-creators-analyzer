from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rrss_creatos_analyzer.apps.core.models import BaseModel


@auditlog.register()
class ExportJob(BaseModel):
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="export_jobs",
        verbose_name=_("Solicitado Por"),
    )
    report_type = models.CharField(
        _("Tipo de Reporte"),
        max_length=50,
        default="streams",
    )
    export_format = models.CharField(_("Formato"), max_length=10, default="csv")
    status = models.CharField(
        _("Estado"),
        max_length=20,
        default="completed",
        db_index=True,
    )
    rows_exported = models.PositiveIntegerField(_("Filas Exportadas"), default=0)
    file_path = models.CharField(_("Ruta de Archivo"), max_length=500, blank=True)
    filter_params = models.JSONField(
        _("Parámetros de Filtro"),
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = _("Trabajo de Exportación")
        verbose_name_plural = _("Trabajos de Exportación")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.report_type}.{self.export_format} ({self.rows_exported} filas)"

    def get_absolute_url(self) -> str:
        return reverse("exports:export_detail", kwargs={"pk": self.pk})
