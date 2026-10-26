from decimal import Decimal

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.choices import PublicationStatus
from rrss_creatos_analyzer.apps.core.choices import PublicationType
from rrss_creatos_analyzer.apps.core.choices import VideoFormat
from rrss_creatos_analyzer.apps.core.choices import VideoRelationType
from rrss_creatos_analyzer.apps.core.choices import VideoStatus
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Channel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.imports.models import ImportBatch
from rrss_creatos_analyzer.apps.streams.models import StreamingSession


@auditlog.register()
class Video(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name=_("Creador"),
    )
    assigned_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_videos",
        verbose_name=_("Editor Asignado"),
    )
    title = models.CharField(_("Título del Video"), max_length=255)
    internal_code = models.CharField(_("Código Interno"), max_length=100, blank=True)
    internal_name = models.CharField(_("Nombre Interno"), max_length=150, blank=True)
    description = models.TextField(_("Descripción / Notas"), blank=True)
    category = models.CharField(
        _("Categoría"),
        max_length=100,
        default="General",
        db_index=True,
    )
    content_format = models.CharField(
        _("Formato de Contenido"),
        max_length=30,
        choices=VideoFormat.choices,
        default=VideoFormat.LONG_FORM,
    )
    duration_seconds = models.PositiveIntegerField(_("Duración (Segundos)"), default=0)

    production_cost = models.DecimalField(
        _("Costo de Producción ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    editing_cost = models.DecimalField(
        _("Costo de Edición ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    thumbnail_cost = models.DecimalField(
        _("Costo de Miniatura ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_production_cost = models.DecimalField(
        _("Costo Total de Producción ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        _("Estado Editorial"),
        max_length=20,
        choices=VideoStatus.choices,
        default=VideoStatus.PUBLISHED,
        db_index=True,
    )
    target_release_date = models.DateField(
        _("Fecha Objetivo de Lanzamiento"),
        null=True,
        blank=True,
    )
    master_asset_url = models.URLField(
        _("URL Archivo Maestro"),
        max_length=500,
        blank=True,
    )

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Video (Activo Maestro)")
        verbose_name_plural = _("Videos (Activos Maestros)")
        ordering = ["-created_at"]
        permissions = [
            (
                "view_all_videos",
                _("Puede ver los videos y publicaciones de todos los creadores"),
            ),
            (
                "view_production_costs",
                _("Puede ver costos de producción, beneficio neto y ROI"),
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(duration_seconds__gte=0) & Q(production_cost__gte=0),
                name="chk_video_costs_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.creator.display_name})"

    def get_absolute_url(self) -> str:
        return reverse("videos:video_detail", kwargs={"pk": self.pk})


@auditlog.register()
class VideoPublication(BaseModel):
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="publications",
        verbose_name=_("Video Maestro"),
    )
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="video_publications",
        verbose_name=_("Creador"),
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_publications",
        verbose_name=_("Canal"),
    )
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_publications",
        verbose_name=_("Lote de Importación"),
    )

    platform = models.CharField(
        _("Plataforma"),
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.YOUTUBE,
        db_index=True,
    )
    platform_post_id = models.CharField(
        _("ID de Post en Plataforma"),
        max_length=150,
        blank=True,
    )
    published_title = models.CharField(
        _("Título Publicado"),
        max_length=255,
        blank=True,
    )
    post_url = models.URLField(_("URL de Publicación"), max_length=500, blank=True)
    thumbnail_url = models.URLField(_("URL de Miniatura"), max_length=500, blank=True)
    publication_type = models.CharField(
        _("Tipo de Publicación"),
        max_length=30,
        choices=PublicationType.choices,
        default=PublicationType.STANDARD,
    )
    published_at = models.DateTimeField(_("Fecha de Publicación"), db_index=True)
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.PUBLISHED,
    )

    views_count = models.PositiveBigIntegerField(_("Vistas"), default=0)
    unique_viewers_count = models.PositiveBigIntegerField(
        _("Espectadores Únicos"),
        default=0,
    )
    impressions_count = models.PositiveBigIntegerField(_("Impresiones"), default=0)
    click_through_rate = models.DecimalField(
        _("CTR (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    likes_count = models.PositiveIntegerField(_("Likes"), default=0)
    dislikes_count = models.PositiveIntegerField(_("Dislikes"), default=0)
    comments_count = models.PositiveIntegerField(_("Comentarios"), default=0)
    shares_count = models.PositiveIntegerField(_("Compartidos"), default=0)
    saves_count = models.PositiveIntegerField(_("Guardados"), default=0)
    watch_time_hours = models.DecimalField(
        _("Tiempo de Visualización (Horas)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    avg_view_duration_seconds = models.PositiveIntegerField(
        _("Duración Media de Vista (s)"),
        default=0,
    )
    retention_rate_pct = models.DecimalField(
        _("Retención Media (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    engagement_rate = models.DecimalField(
        _("Tasa de Engagement (%)"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    ad_revenue = models.DecimalField(
        _("Ingresos por Anuncios ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    sponsorship_revenue = models.DecimalField(
        _("Ingresos por Patrocinio ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    estimated_revenue = models.DecimalField(
        _("Ingresos Estimados Totales ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    rpm_estimated = models.DecimalField(
        _("RPM Estimado ($)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Publicación de Video")
        verbose_name_plural = _("Publicaciones de Video")
        ordering = ["-published_at"]

    def __str__(self) -> str:
        plat = self.get_platform_display()
        ptype = self.get_publication_type_display()
        return f"{self.video.title} [{plat} - {ptype}]"

    def get_absolute_url(self) -> str:
        return reverse("videos:publication_detail", kwargs={"pk": self.pk})


@auditlog.register()
class VideoRelation(BaseModel):
    source_video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name="outgoing_relations",
        verbose_name=_("Video Origen"),
    )
    target_video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="incoming_relations",
        verbose_name=_("Video Relacionado"),
    )
    target_session = models.ForeignKey(
        StreamingSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="derived_video_relations",
        verbose_name=_("Sesión de Streaming Origen"),
    )
    relation_type = models.CharField(
        _("Tipo de Relación"),
        max_length=30,
        choices=VideoRelationType.choices,
        default=VideoRelationType.DERIVED_FROM_LIVE,
    )
    description = models.TextField(_("Descripción"), blank=True)
    timestamp_start_seconds = models.PositiveIntegerField(
        _("Segundo Inicio"),
        null=True,
        blank=True,
    )
    timestamp_end_seconds = models.PositiveIntegerField(
        _("Segundo Fin"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Relación de Video")
        verbose_name_plural = _("Relaciones de Video")
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(target_video__isnull=False)
                | Q(target_session__isnull=False),
                name="chk_vrel_target_present",
            ),
        ]

    def __str__(self) -> str:
        target = self.target_video or self.target_session
        rtype = self.get_relation_type_display()
        return f"{self.source_video.title} -> {target} ({rtype})"

    def get_absolute_url(self) -> str:
        return reverse("videos:relation_detail", kwargs={"pk": self.pk})
