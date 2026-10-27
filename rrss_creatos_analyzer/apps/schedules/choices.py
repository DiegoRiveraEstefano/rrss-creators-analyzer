from django.db import models
from django.utils.translation import gettext_lazy as _


class DayOfWeek(models.IntegerChoices):
    MONDAY = 0, _("Lunes")
    TUESDAY = 1, _("Martes")
    WEDNESDAY = 2, _("Miércoles")
    THURSDAY = 3, _("Jueves")
    FRIDAY = 4, _("Viernes")
    SATURDAY = 5, _("Sábado")
    SUNDAY = 6, _("Domingo")


class ScheduleSlotStatus(models.TextChoices):
    SCHEDULED = "scheduled", _("Programado")
    COMPLETED = "completed", _("Cumplido")
    PARTIAL = "partial", _("Cumplimiento Parcial")
    LATE = "late", _("Inicio Retrasado")
    MISSED = "missed", _("Inasistencia")
    JUSTIFIED_ABSENCE = "justified", _("Ausencia Justificada")
    CANCELLED = "cancelled", _("Cancelado")
    RESCHEDULED = "rescheduled", _("Reprogramado")


class ScheduleExceptionReason(models.TextChoices):
    MEDICAL = "medical", _("Licencia Médica / Salud")
    VACATION = "vacation", _("Vacaciones / Descanso Planificado")
    TECHNICAL = "technical", _("Incidencia Técnica / Conectividad")
    AGENCY_EVENT = "agency_event", _("Evento Oficial / Compromiso de Agencia")
    PERSONAL = "personal", _("Asunto Personal Justificado")
    OTHER = "other", _("Otro Motivo")
