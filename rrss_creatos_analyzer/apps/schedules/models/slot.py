from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.schedules.choices import ScheduleSlotStatus
from rrss_creatos_analyzer.apps.schedules.models.pattern import CreatorSchedulePattern
from rrss_creatos_analyzer.apps.streams.models import StreamingSession


@auditlog.register()
class CreatorScheduleSlot(BaseModel):
    """Cita o bloque específico de transmisión fechado en el calendario."""

    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="schedule_slots",
        verbose_name=_("Creador"),
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_slots",
        verbose_name=_("Canal"),
    )
    schedule_pattern = models.ForeignKey(
        CreatorSchedulePattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_slots",
        verbose_name=_("Pauta Recurrente Origen"),
    )
    scheduled_date = models.DateField(_("Fecha Programada"), db_index=True)
    scheduled_start_time = models.TimeField(_("Hora Pactada de Inicio"))
    scheduled_end_time = models.TimeField(_("Hora Pactada de Fin"))
    planned_duration_minutes = models.PositiveIntegerField(
        _("Duración Pactada (Minutos)"),
        default=120,
    )
    planned_hours = models.DecimalField(
        _("Horas Pactadas"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("2.00"),
    )
    title = models.CharField(
        _("Título / Dinámica"),
        max_length=255,
        default="Stream Programado",
    )
    category_or_game = models.CharField(
        _("Categoría / Juego"),
        max_length=150,
        default="Just Chatting",
    )
    status = models.CharField(
        _("Estado de Cumplimiento"),
        max_length=25,
        choices=ScheduleSlotStatus.choices,
        default=ScheduleSlotStatus.SCHEDULED,
        db_index=True,
    )
    is_mandatory = models.BooleanField(_("Cómputo Obligatorio"), default=True)

    actual_streaming_session = models.ForeignKey(
        StreamingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciled_schedule_slots",
        verbose_name=_("Sesión de Stream Reconciliada"),
    )
    actual_start_datetime = models.DateTimeField(
        _("Fecha/Hora Real de Inicio"),
        null=True,
        blank=True,
    )
    actual_end_datetime = models.DateTimeField(
        _("Fecha/Hora Real de Fin"),
        null=True,
        blank=True,
    )
    actual_duration_minutes = models.PositiveIntegerField(
        _("Duración Real (Minutos)"),
        default=0,
    )
    actual_hours = models.DecimalField(
        _("Horas Reales Transmitidas"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    start_delay_minutes = models.IntegerField(
        _("Retraso de Inicio (Minutos)"),
        default=0,
        help_text=_("Minutos transcurridos entre hora pactada y streaming real."),
    )
    compliance_rate_pct = models.DecimalField(
        _("Porcentaje de Cumplimiento de Horas (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.TextField(_("Notas / Observaciones"), blank=True)

    history = HistoricalRecords()

    class Meta:
        app_label = "schedules"
        verbose_name = _("Cita Programada de Transmisión")
        verbose_name_plural = _("Citas Programadas de Transmisión")
        ordering = ["scheduled_date", "scheduled_start_time"]
        constraints = [
            models.CheckConstraint(
                condition=Q(planned_hours__gte=Decimal("0.00")),
                name="chk_slot_planned_hours_positive",
            ),
            models.UniqueConstraint(
                fields=["creator", "scheduled_date", "scheduled_start_time"],
                name="unique_creator_scheduled_slot_time",
            ),
        ]

    @property
    def weekly_pattern(self) -> CreatorSchedulePattern | None:
        return self.schedule_pattern

    def __str__(self) -> str:
        date_str = self.scheduled_date.strftime("%d/%m/%Y")
        times = f"{self.scheduled_start_time}-{self.scheduled_end_time}"
        status_lbl = self.get_status_display()
        return f"{self.creator.display_name} - {date_str} {times} [{status_lbl}]"

    def get_absolute_url(self) -> str:
        return reverse("schedules:slot_detail", kwargs={"pk": self.pk})
