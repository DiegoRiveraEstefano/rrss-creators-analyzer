from django.db import models
from django.utils.translation import gettext_lazy as _


class PlatformType(models.TextChoices):
    TWITCH = "twitch", _("Twitch")
    YOUTUBE = "youtube", _("YouTube")
    KICK = "kick", _("Kick")
    TIKTOK = "tiktok", _("TikTok")
    INSTAGRAM = "instagram", _("Instagram")
    X = "x", _("X (Twitter)")


class CreatorStatus(models.TextChoices):
    ONBOARDING = "onboarding", _("Onboarding")
    ACTIVE = "active", _("Activo")
    INACTIVE = "inactive", _("Inactivo")
    ON_LEAVE = "on_leave", _("En Pausa / Licencia")
    SUSPENDED = "suspended", _("Suspendido")
    TERMINATED = "terminated", _("Finalizado")


class CreatorTier(models.TextChoices):
    ROOKIE = "rookie", _("Rookie")
    STANDARD = "standard", _("Estándar")
    PARTNER = "partner", _("Partner")
    ELITE = "elite", _("Elite")
    AMBASSADOR = "ambassador", _("Embajador")


class ChannelStatus(models.TextChoices):
    ACTIVE = "active", _("Activo")
    DEMONETIZED = "demonetized", _("Desmonetizado")
    SHADOWBANNED = "shadowbanned", _("Shadowbanned")
    SUSPENDED = "suspended", _("Suspendido")
    BANNED = "banned", _("Baneado")
    ARCHIVED = "archived", _("Archivado")


class ContractStatus(models.TextChoices):
    DRAFT = "draft", _("Borrador")
    ACTIVE = "active", _("Activo")
    EXPIRED = "expired", _("Expirado")
    TERMINATED = "terminated", _("Rescindido")
    RENEWED = "renewed", _("Renovado")


class TeamResponsibility(models.TextChoices):
    TALENT_MANAGER = "talent_manager", _("Talent Manager")
    VIDEO_EDITOR = "video_editor", _("Editor de Video")
    THUMBNAIL_DESIGNER = "thumbnail_designer", _("Diseñador de Miniaturas")
    ANALYST = "analyst", _("Analista de Datos")
    MODERATOR = "moderator", _("Moderador Principal")


class VideoStatus(models.TextChoices):
    IDEA = "idea", _("Idea")
    SCRIPTING = "scripting", _("Guion")
    RECORDING = "recording", _("Grabación")
    EDITING = "editing", _("Edición")
    REVIEW = "review", _("Revisión")
    READY = "ready", _("Listo")
    PUBLISHED = "published", _("Publicado")
    ARCHIVED = "archived", _("Archivado")


class VideoFormat(models.TextChoices):
    LONG_FORM = "long_form", _("Video Largo (VOD/Main)")
    SHORT_VERTICAL = "short_vertical", _("Short / Vertical")
    VOD_HIGHLIGHT = "vod_highlight", _("Resubido / Highlight de Stream")
    CLIP = "clip", _("Clip Corto")
    PODCAST = "podcast", _("Podcast")
    TEASER = "teaser", _("Teaser / Promo")


class PublicationType(models.TextChoices):
    STANDARD = "standard", _("Estándar")
    SHORT = "short", _("YouTube Short")
    REEL = "reel", _("Instagram Reel")
    TIKTOK = "tiktok", _("TikTok Video")
    VOD = "vod", _("VOD Completo")
    CLIP = "clip", _("Clip")
    TEASER = "teaser", _("Teaser")


class PublicationStatus(models.TextChoices):
    SCHEDULED = "scheduled", _("Programado")
    PUBLISHED = "published", _("Publicado")
    UNLISTED = "unlisted", _("No listado")
    PRIVATE = "private", _("Privado")
    DEMONETIZED = "demonetized", _("Desmonetizado")
    REMOVED = "removed", _("Eliminado")
    STRUCK = "struck", _("Con Strike")


class VideoRelationType(models.TextChoices):
    DERIVED_FROM_LIVE = "derived_from_live", _("Derivado de Stream en Vivo")
    CONTINUATION = "continuation", _("Continuación")
    SEQUEL = "sequel", _("Secuela")
    CLIP = "clip", _("Clip Extraído")
    SPIN_OFF = "spin_off", _("Spin-off")
    REFERENCE = "reference", _("Referencia")
    REUPLOAD = "reupload", _("Resubida")


class AlertType(models.TextChoices):
    DMCA_STRIKE = "dmca_strike", _("Strike de DMCA")
    COPYRIGHT_CLAIM = "copyright_claim", _("Reclamo de Copyright")
    TOS_VIOLATION = "tos_violation", _("Violación de TOS")
    COMMUNITY_STRIKE = "community_guideline_strike", _("Strike de Normas de Comunidad")
    DEMONETIZATION = "demonetization", _("Desmonetización")
    TEMPORARY_BAN = "temporary_ban", _("Suspensión Temporal")
    UNUSUAL_CCV_DROP = "unusual_ccv_drop", _("Caída Inusual de CCV")
    SUSPICIOUS_TRAFFIC = "suspicious_bot_traffic", _("Tráfico Sospechoso / Bots")
    QUOTA_MISSED = "quota_missed", _("Incumplimiento de Cuota Mensual")


class AlertSeverity(models.TextChoices):
    INFO = "info", _("Informativa")
    WARNING = "warning", _("Advertencia")
    CRITICAL = "critical", _("Crítica")


class AlertStatus(models.TextChoices):
    ACTIVE = "active", _("Activa")
    INVESTIGATING = "investigating", _("En Investigación")
    APPEALED = "appealed", _("Apelada")
    RESOLVED = "resolved", _("Resuelta")
    EXPIRED = "expired", _("Expirada")
    DISMISSED = "dismissed", _("Descartada")


class ImportBatchType(models.TextChoices):
    STREAMS = "streams", _("Sesiones de Streaming")
    VIDEOS = "videos", _("Activos de Video")
    PUBLICATIONS = "publications", _("Publicaciones de Video")
    CHANNELS = "channels", _("Canales")
    ALERTS = "alerts", _("Alertas de Canal")
    MIXED = "mixed", _("Mixto")


class ImportStatus(models.TextChoices):
    PENDING = "pending", _("Pendiente")
    PROCESSING = "processing", _("Procesando")
    COMPLETED = "completed", _("Completado")
    PARTIAL = "partial", _("Completado con Errores")
    FAILED = "failed", _("Fallido")
    ROLLED_BACK = "rolled_back", _("Revertido")


class CampaignStatus(models.TextChoices):
    PROPOSAL = "proposal", _("Propuesta")
    NEGOTIATING = "negotiating", _("En Negociación")
    ACTIVE = "active", _("Activa")
    COMPLETED = "completed", _("Completada")
    INVOICED = "invoiced", _("Facturada")
    PAID = "paid", _("Pagada")
    CANCELLED = "cancelled", _("Cancelada")


class DeliverableType(models.TextChoices):
    SPONSORED_STREAM = "sponsored_stream", _("Stream Patrocinado")
    DEDICATED_VIDEO = "dedicated_video", _("Video Dedicado")
    INTEGRATED_AD_READ = "integrated_ad_read", _("Mención Integrada (Ad Read)")
    SHORT_OR_REEL = "short_or_reel", _("Short / Reel / TikTok")
    SOCIAL_POST = "social_post", _("Post en Redes Sociales")


class DeliverableStatus(models.TextChoices):
    PENDING = "pending", _("Pendiente")
    IN_PROGRESS = "in_progress", _("En Progreso")
    SUBMITTED = "submitted", _("Enviado a Revisión")
    APPROVED = "approved", _("Aprobado")
    PUBLISHED = "published", _("Publicado")
    REJECTED = "rejected", _("Rechazado")


class PayoutStatus(models.TextChoices):
    DRAFT = "draft", _("Borrador")
    PENDING_APPROVAL = "pending_approval", _("Pendiente de Aprobación")
    APPROVED = "approved", _("Aprobado")
    PAID = "paid", _("Pagado")
    DISPUTED = "disputed", _("En Disputa")
    CANCELLED = "cancelled", _("Cancelado")
