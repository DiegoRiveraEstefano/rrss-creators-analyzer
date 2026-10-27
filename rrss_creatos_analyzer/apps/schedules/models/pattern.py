from auditlog.registry import auditlog
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.schedules.rrule_utils import rrule_to_human
from rrss_creatos_analyzer.apps.schedules.rrule_utils import validate_rrule


@auditlog.register()
class CreatorSchedulePattern(BaseModel):
    """Pauta recurrente de horarios gobernada por reglas RFC 5545 (RRULE)."""

    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="schedule_patterns",
        verbose_name=_("Creador"),
    )
    title = models.CharField(
        _("Título del Patrón"),
        max_length=150,
        blank=True,
        help_text=_("Nombre descriptivo, ej. 'Streams Nocturnos Just Chatting'"),
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_patterns",
        verbose_name=_("Canal"),
    )
    platform = models.CharField(
        _("Plataforma"),
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.TWITCH,
        db_index=True,
    )
    rrule = models.CharField(
        _("Regla de Recurrencia (RRULE)"),
        max_length=255,
        default="FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1",
        help_text=_(
            "Especificación RFC 5545 (ej. FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1)",
        ),
    )
    start_time = models.TimeField(_("Hora de Inicio Estipulada"))
    end_time = models.TimeField(_("Hora de Fin Estipulada"))
    planned_duration_minutes = models.PositiveIntegerField(
        _("Duración Estipulada (Minutos)"),
        default=120,
    )
    category_or_game = models.CharField(
        _("Categoría / Temática"),
        max_length=150,
        default="Just Chatting",
    )
    is_mandatory = models.BooleanField(
        _("Cómputo Obligatorio"),
        default=True,
        help_text=_("Indica si este patrón genera slots computables contractualmente."),
    )
    effective_from = models.DateField(_("Vigente Desde"))
    effective_until = models.DateField(
        _("Vigente Hasta"),
        null=True,
        blank=True,
        help_text=_("Dejar vacío para vigencia indefinida."),
    )
    is_active = models.BooleanField(_("Activo"), default=True, db_index=True)
    notes = models.TextField(_("Notas"), blank=True)

    history = HistoricalRecords()

    class Meta:
        app_label = "schedules"
        verbose_name = _("Pauta Recurrente de Creador")
        verbose_name_plural = _("Pautas Recurrentes de Creadores")
        ordering = ["start_time"]
        constraints = [
            models.CheckConstraint(
                condition=Q(planned_duration_minutes__gt=0),
                name="chk_pattern_planned_duration_gt_0",
            ),
            models.CheckConstraint(
                condition=Q(effective_until__isnull=True)
                | Q(effective_until__gte=F("effective_from")),
                name="chk_pattern_effective_dates_coherent",
            ),
        ]

    @property
    def human_recurrence(self) -> str:
        return rrule_to_human(self.rrule)

    def clean(self) -> None:
        super().clean()
        validate_rrule(self.rrule)
        if self.effective_until and self.effective_until < self.effective_from:
            msg = _("La fecha de fin de vigencia no puede ser anterior a la de inicio.")
            raise ValidationError(msg)

    def __str__(self) -> str:
        label = self.title or self.human_recurrence
        times = f"{self.start_time}-{self.end_time}"
        return f"{self.creator.display_name} - {label} ({times})"

    def get_absolute_url(self) -> str:
        return reverse("schedules:pattern_detail", kwargs={"pk": self.pk})


# Alias de compatibilidad retroactiva
CreatorWeeklySchedule = CreatorSchedulePattern
