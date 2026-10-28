from decimal import Decimal

from auditlog.registry import auditlog
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.imports.models import ImportBatch


@auditlog.register()
class StreamingSession(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="streaming_sessions",
        verbose_name=_("Creador"),
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="streaming_sessions",
        verbose_name=_("Canal"),
    )
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="streaming_sessions",
        verbose_name=_("Lote de Importación"),
    )

    external_stream_id = models.CharField(
        _("ID Externo del Stream"),
        max_length=150,
        blank=True,
    )
    session_title = models.CharField(
        _("Título de la Sesión"),
        max_length=255,
        default="Live Stream",
    )
    game_or_category = models.CharField(
        _("Categoría / Juego"),
        max_length=150,
        default="Just Chatting",
        db_index=True,
    )
    platform = models.CharField(
        _("Plataforma"),
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.TWITCH,
        db_index=True,
    )
    stream_url = models.URLField(_("URL del Stream"), max_length=500, blank=True)
    vod_url = models.URLField(_("URL del VOD"), max_length=500, blank=True)

    streamed_at = models.DateTimeField(_("Fecha/Hora de Transmisión"), db_index=True)
    ended_at = models.DateTimeField(_("Fecha/Hora de Fin"), null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(_("Duración (Segundos)"), default=0)
    hours_streamed = models.DecimalField(
        _("Horas Transmitidas"),
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    peak_viewers = models.PositiveIntegerField(
        _("Pico de Espectadores (Peak)"),
        default=0,
    )
    avg_ccv = models.PositiveIntegerField(_("Media de Espectadores (CCV)"), default=0)
    unique_viewers = models.PositiveIntegerField(_("Espectadores Únicos"), default=0)
    live_views_count = models.PositiveIntegerField(_("Vistas en Vivo"), default=0)
    chat_messages_count = models.PositiveIntegerField(_("Mensajes en Chat"), default=0)
    unique_chatters_count = models.PositiveIntegerField(_("Chatters Únicos"), default=0)
    new_followers = models.PositiveIntegerField(_("Nuevos Seguidores"), default=0)
    new_subscriptions = models.PositiveIntegerField(
        _("Nuevas Suscripciones"),
        default=0,
    )
    gifted_subscriptions = models.PositiveIntegerField(
        _("Suscripciones Regaladas"),
        default=0,
    )
    raids_received = models.PositiveIntegerField(_("Raids Recibidos"), default=0)

    ad_revenue = models.DecimalField(
        _("Ingresos por Publicidad ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    subs_revenue = models.DecimalField(
        _("Ingresos por Suscripciones ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    donations_revenue = models.DecimalField(
        _("Ingresos por Donaciones ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    bits_or_gifts_revenue = models.DecimalField(
        _("Ingresos por Bits / Regalos ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    sponsorship_revenue = models.DecimalField(
        _("Ingresos por Patrocinio Directo ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_earnings = models.DecimalField(
        _("Ingresos Totales ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    earnings_per_hour = models.DecimalField(
        _("Ingresos por Hora ($/h)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    is_sponsored = models.BooleanField(_("Es Stream Patrocinado"), default=False)
    notes = models.TextField(_("Notas"), blank=True)

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Sesión de Streaming")
        verbose_name_plural = _("Sesiones de Streaming")
        ordering = ["-streamed_at"]
        permissions = [
            ("view_all_sessions", _("Puede ver las sesiones de todos los creadores")),
            ("export_sessions", _("Puede exportar reportes de sesiones")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(duration_seconds__gte=0)
                    & Q(peak_viewers__gte=0)
                    & Q(avg_ccv__gte=0)
                    & Q(ad_revenue__gte=0)
                    & Q(subs_revenue__gte=0)
                    & Q(donations_revenue__gte=0)
                    & Q(bits_or_gifts_revenue__gte=0)
                    & Q(sponsorship_revenue__gte=0)
                    & Q(total_earnings__gte=0)
                ),
                name="chk_stream_metrics_non_negative",
            ),
            models.UniqueConstraint(
                fields=["creator", "platform", "external_stream_id"],
                condition=Q(external_stream_id__gt=""),
                name="uq_stream_creator_platform_ext_id",
            ),
        ]

    def __str__(self) -> str:
        dt = f"{self.streamed_at:%Y-%m-%d}"
        return f"{self.session_title} - {self.creator.display_name} ({dt})"

    def get_absolute_url(self) -> str:
        return reverse("streams:session_detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        super().clean()
        if self.streamed_at and self.ended_at and self.ended_at < self.streamed_at:
            raise ValidationError(
                {
                    "ended_at": _(
                        "La fecha/hora de fin no puede ser anterior a la de inicio.",
                    ),
                },
            )
        if self.avg_ccv > self.peak_viewers:
            raise ValidationError(
                {
                    "peak_viewers": _(
                        "El pico de espectadores debe ser mayor o igual "
                        "a la media de espectadores (CCV).",
                    ),
                },
            )
        if self.is_sponsored and self.sponsorship_revenue <= Decimal("0.00"):
            raise ValidationError(
                {
                    "sponsorship_revenue": _(
                        "Una sesión marcada como patrocinada debe contar con "
                        "un ingreso de patrocinio mayor a cero.",
                    ),
                },
            )


@auditlog.register()
class SessionSegment(BaseModel):
    session = models.ForeignKey(
        StreamingSession,
        on_delete=models.CASCADE,
        related_name="segments",
        verbose_name=_("Sesión de Streaming"),
    )
    game_or_category = models.CharField(_("Categoría / Juego"), max_length=150)
    start_offset_seconds = models.PositiveIntegerField(
        _("Inicio desde arranque (s)"),
        default=0,
    )
    duration_seconds = models.PositiveIntegerField(_("Duración (s)"), default=0)
    avg_ccv = models.PositiveIntegerField(_("CCV Promedio"), default=0)
    peak_viewers = models.PositiveIntegerField(_("Pico de Espectadores"), default=0)

    class Meta:
        verbose_name = _("Segmento de Sesión")
        verbose_name_plural = _("Segmentos de Sesión")
        ordering = ["session", "start_offset_seconds"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(duration_seconds__gte=0)
                    & Q(start_offset_seconds__gte=0)
                    & Q(avg_ccv__gte=0)
                    & Q(peak_viewers__gte=0)
                ),
                name="chk_segment_metrics_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.session.session_title} - {self.game_or_category}"

    def get_absolute_url(self) -> str:
        return reverse("streams:segment_detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        super().clean()
        if self.avg_ccv > self.peak_viewers:
            raise ValidationError(
                {
                    "peak_viewers": _(
                        "El pico de espectadores debe ser mayor o igual "
                        "al CCV promedio.",
                    ),
                },
            )
        if (
            self.session_id
            and self.session.duration_seconds > 0
            and self.start_offset_seconds + self.duration_seconds
            > self.session.duration_seconds
        ):
            raise ValidationError(
                {
                    "duration_seconds": _(
                        "El rango del segmento excede la duración total de la sesión.",
                    ),
                },
            )
