from auditlog.registry import auditlog
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleExceptionReason


@auditlog.register()
class ScheduleException(BaseModel):
    """Excepciones de agenda: vacaciones, licencias, feriados o fallas técnicas."""

    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="schedule_exceptions",
        verbose_name=_("Creador"),
    )
    reason_type = models.CharField(
        _("Tipo de Motivo"),
        max_length=25,
        choices=ScheduleExceptionReason.choices,
        default=ScheduleExceptionReason.PERSONAL,
        db_index=True,
    )
    title = models.CharField(_("Título / Resumen"), max_length=200)
    description = models.TextField(_("Detalle / Justificación"), blank=True)
    start_date = models.DateField(_("Fecha Inicio"), db_index=True)
    end_date = models.DateField(_("Fecha Fin"), db_index=True)
    is_approved = models.BooleanField(
        _("Aprobada"),
        default=False,
        db_index=True,
        help_text=_("Una excepción aprobada conmuta los slots al estado Justificado."),
    )
    approved_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_schedule_exceptions",
        verbose_name=_("Aprobado Por"),
    )
    approved_at = models.DateTimeField(
        _("Fecha/Hora de Aprobación"),
        null=True,
        blank=True,
    )
    document_url = models.URLField(
        _("URL Comprobante o Licencia"),
        blank=True,
        help_text=_("Enlace a certificado médico o documento respaldatorio."),
    )

    history = HistoricalRecords()

    class Meta:
        app_label = "schedules"
        verbose_name = _("Excepción / Permiso de Agenda")
        verbose_name_plural = _("Excepciones y Permisos de Agenda")
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F("start_date")),
                name="chk_exception_coherent_dates",
            ),
        ]

    def __str__(self) -> str:
        range_str = f"{self.start_date} al {self.end_date}"
        return f"{self.creator.display_name} - {self.title} ({range_str})"

    def get_absolute_url(self) -> str:
        return reverse("schedules:exception_detail", kwargs={"pk": self.pk})
