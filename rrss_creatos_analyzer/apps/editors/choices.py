from django.db import models
from django.utils.translation import gettext_lazy as _


class EditorStatus(models.TextChoices):
    ACTIVE = "active", _("Activo / Disponible")
    BUSY = "busy", _("Ocupado / Capacidad Máxima")
    ON_LEAVE = "on_leave", _("En Pausa / De Vacaciones")
    INACTIVE = "inactive", _("Inactivo")


class EditorType(models.TextChoices):
    IN_HOUSE = "in_house", _("Plantilla / In-House")
    FREELANCER = "freelancer", _("Freelancer / Contratista")
    AGENCY = "agency", _("Agencia de Edición Externa")
    STUDIO = "studio", _("Estudio de Postproducción")


class EditorSpecialty(models.TextChoices):
    LONG_FORM = "long_form", _("Video Largo / YouTube")
    SHORTS_REELS = "shorts_reels", _("Shorts / Reels / TikTok")
    HIGHLIGHTS = "highlights", _("Highlights / Clips de Stream")
    MOTION_GRAPHICS = "motion_graphics", _("Motion Graphics / VFX")
    THUMBNAILS = "thumbnails", _("Diseño de Miniaturas")
    COLOR_SOUND = "color_sound", _("Color Grading y Sonido")
    ALL_ROUNDER = "all_rounder", _("Generalista / Todo Formato")


class RateModel(models.TextChoices):
    PER_VIDEO = "per_video", _("Por Video Largo Terminado")
    PER_SHORT = "per_short", _("Por Short / Formato Vertical")
    HOURLY = "hourly", _("Por Hora Trabajada")
    PER_MINUTE = "per_minute", _("Por Minuto de Video Final")
    MONTHLY_RETAINER = "monthly_retainer", _("Retainer Fijo Mensual")


class EditorAssignmentRole(models.TextChoices):
    LEAD_EDITOR = "lead_editor", _("Editor Principal")
    SECONDARY_EDITOR = "secondary_editor", _("Editor Secundario / Apoyo")
    SHORTS_EDITOR = "shorts_editor", _("Editor de Shorts / Vertical")
    THUMBNAIL_DESIGNER = "thumbnail_designer", _("Diseñador de Miniaturas")
    COLORIST_SOUND = "colorist_sound", _("Colorista / Post Sonido")


class AssignmentStatus(models.TextChoices):
    ACTIVE = "active", _("Activa")
    PAUSED = "paused", _("Pausada")
    ENDED = "ended", _("Finalizada")


class TaskStatus(models.TextChoices):
    DRAFT = "draft", _("Borrador / Preparación")
    ASSIGNED = "assigned", _("Asignada al Editor")
    IN_PROGRESS = "in_progress", _("En Proceso de Edición")
    IN_REVIEW = "in_review", _("En Revisión (Corte Enviado)")
    REVISION_REQUESTED = "revision_requested", _("Cambios Solicitados")
    APPROVED = "approved", _("Aprobada")
    COMPLETED = "completed", _("Completada / Finalizada")
    CANCELLED = "cancelled", _("Cancelada")


class TaskPriority(models.TextChoices):
    LOW = "low", _("Baja")
    MEDIUM = "medium", _("Media")
    HIGH = "high", _("Alta")
    URGENT = "urgent", _("Urgente")


class TaskType(models.TextChoices):
    LONG_FORM_EDIT = "long_form_edit", _("Edición Video Largo")
    SHORT_VERTICAL = "short_vertical", _("Edición Short / Reel")
    VOD_CUT = "vod_cut", _("Corte de Transmisión / VOD")
    HIGHLIGHT_REEL = "highlight_reel", _("Recopilación / Highlight")
    THUMBNAIL = "thumbnail", _("Miniatura")
    REVISION = "revision", _("Revisión / Ajuste Menor")


class RevisionStatus(models.TextChoices):
    PENDING_REVIEW = "pending_review", _("Pendiente de Revisión")
    CHANGES_REQUESTED = "changes_requested", _("Cambios Requeridos")
    APPROVED = "approved", _("Aprobado")
