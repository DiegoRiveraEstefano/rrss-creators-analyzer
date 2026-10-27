from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.choices import ImportBatchType
from rrss_creatos_analyzer.apps.core.choices import ImportStatus
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.models import BaseModel


@auditlog.register()
class ImportBatch(BaseModel):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_batches",
        verbose_name=_("Subido Por"),
    )
    batch_type = models.CharField(
        _("Tipo de Lote"),
        max_length=30,
        choices=ImportBatchType.choices,
        default=ImportBatchType.STREAMS,
    )
    source_platform = models.CharField(
        _("Plataforma Origen"),
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.TWITCH,
    )
    filename = models.CharField(_("Nombre de Archivo"), max_length=255)
    file_path = models.CharField(_("Ruta de Archivo"), max_length=500, blank=True)
    file_hash_sha256 = models.CharField(_("Hash SHA-256"), max_length=64, blank=True)

    total_rows = models.PositiveIntegerField(_("Total Filas"), default=0)
    valid_rows = models.PositiveIntegerField(_("Filas Válidas"), default=0)
    created_rows = models.PositiveIntegerField(_("Filas Creadas"), default=0)
    updated_rows = models.PositiveIntegerField(_("Filas Actualizadas"), default=0)
    skipped_rows = models.PositiveIntegerField(_("Filas Omitidas"), default=0)
    error_count = models.PositiveIntegerField(_("Errores"), default=0)

    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=ImportStatus.choices,
        default=ImportStatus.COMPLETED,
        db_index=True,
    )
    error_summary = models.JSONField(_("Resumen de Errores"), default=list, blank=True)
    started_at = models.DateTimeField(_("Iniciado el"), auto_now_add=True)
    completed_at = models.DateTimeField(_("Completado el"), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Lote de Importación")
        verbose_name_plural = _("Lotes de Importación")
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_rows__gte=0)
                & Q(valid_rows__gte=0)
                & Q(error_count__gte=0),
                name="chk_import_counts_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"#{self.pk} - {self.filename} ({self.get_status_display()})"

    def get_absolute_url(self) -> str:
        return reverse("imports:batch_detail", kwargs={"pk": self.pk})
