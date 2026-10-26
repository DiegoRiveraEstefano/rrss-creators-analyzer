from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from rrss_creatos_analyzer.apps.core.choices import ChannelStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorStatus
from rrss_creatos_analyzer.apps.core.choices import CreatorTier
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.models import BaseModel


@auditlog.register()
class Creator(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="creator_profile",
        verbose_name=_("Cuenta de Usuario"),
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_creators",
        verbose_name=_("Manager Principal"),
    )
    display_name = models.CharField(_("Nombre Público"), max_length=150)
    handle = models.CharField(
        _("Handle (@)"),
        max_length=100,
        unique=True,
        db_index=True,
    )
    slug = models.SlugField(_("Slug"), max_length=120, unique=True)
    legal_full_name = models.CharField(
        _("Nombre Legal Completo"),
        max_length=255,
        blank=True,
    )
    contact_email = models.EmailField(_("Email de Contacto"), blank=True)
    country_code = models.CharField(_("País (ISO-2)"), max_length=2, blank=True)
    language_code = models.CharField(_("Idioma"), max_length=10, default="es")
    avatar_url = models.URLField(_("Avatar URL"), max_length=500, blank=True)
    banner_url = models.URLField(_("Banner URL"), max_length=500, blank=True)
    bio = models.TextField(_("Biografía"), blank=True)
    main_category = models.CharField(
        _("Categoría Principal"),
        max_length=120,
        default="General",
    )
    primary_platform = models.CharField(
        _("Plataforma Principal"),
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.TWITCH,
        db_index=True,
    )
    tier = models.CharField(
        _("Nivel / Tier"),
        max_length=20,
        choices=CreatorTier.choices,
        default=CreatorTier.STANDARD,
        db_index=True,
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=CreatorStatus.choices,
        default=CreatorStatus.ACTIVE,
        db_index=True,
    )
    joined_company_at = models.DateField(_("Fecha de Ingreso"), null=True, blank=True)
    left_company_at = models.DateField(_("Fecha de Baja"), null=True, blank=True)
    internal_notes = models.TextField(_("Notas Internas"), blank=True)

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Creador")
        verbose_name_plural = _("Creadores")
        ordering = ["display_name"]
        permissions = [
            ("view_all_creators", _("Puede ver todos los creadores de la compañía")),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} (@{self.handle})"

    def get_absolute_url(self) -> str:
        return reverse("creators:creator_detail", kwargs={"pk": self.pk})


@auditlog.register()
class Channel(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="channels",
        verbose_name=_("Creador"),
    )
    platform = models.CharField(
        _("Plataforma"),
        max_length=20,
        choices=PlatformType.choices,
        db_index=True,
    )
    platform_channel_id = models.CharField(
        _("ID de Canal en Plataforma"),
        max_length=150,
    )
    handle = models.CharField(_("Handle del Canal"), max_length=150, blank=True)
    channel_name = models.CharField(_("Nombre del Canal"), max_length=150, blank=True)
    channel_url = models.URLField(_("URL del Canal"), max_length=500, blank=True)

    is_primary = models.BooleanField(_("Canal Principal"), default=False)
    is_verified = models.BooleanField(_("Verificado"), default=False)
    is_monetized = models.BooleanField(_("Monetizado"), default=True)
    is_live = models.BooleanField(_("En Vivo Ahora"), default=False, db_index=True)
    status = models.CharField(
        _("Estado del Canal"),
        max_length=20,
        choices=ChannelStatus.choices,
        default=ChannelStatus.ACTIVE,
    )

    followers_count = models.PositiveIntegerField(_("Seguidores"), default=0)
    subscribers_count = models.PositiveIntegerField(_("Suscriptores"), default=0)
    paid_subscribers_count = models.PositiveIntegerField(
        _("Suscriptores de Pago"),
        default=0,
    )
    total_views_count = models.PositiveBigIntegerField(_("Vistas Totales"), default=0)

    sync_enabled = models.BooleanField(_("Sincronización Activa"), default=True)
    last_synced_at = models.DateTimeField(
        _("Última Sincronización"),
        null=True,
        blank=True,
    )
    last_stream_at = models.DateTimeField(_("Último Stream"), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Canal")
        verbose_name_plural = _("Canales")
        ordering = ["creator__display_name", "platform"]
        constraints = [
            models.UniqueConstraint(
                fields=["creator", "platform", "platform_channel_id"],
                name="uq_creator_platform_channel",
            ),
        ]

    def __str__(self) -> str:
        plat = self.get_platform_display()
        return f"{self.creator.display_name} - {plat} ({self.platform_channel_id})"

    def get_absolute_url(self) -> str:
        return reverse("creators:channel_detail", kwargs={"pk": self.pk})


@auditlog.register()
class ChannelSnapshot(BaseModel):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="snapshots",
        verbose_name=_("Canal"),
    )
    snapshot_date = models.DateField(_("Fecha de Snapshot"), db_index=True)
    followers_count = models.PositiveIntegerField(_("Seguidores"), default=0)
    followers_delta = models.IntegerField(_("Variación Seguidores"), default=0)
    subscribers_count = models.PositiveIntegerField(_("Suscriptores"), default=0)
    subscribers_delta = models.IntegerField(_("Variación Suscriptores"), default=0)
    paid_subscribers_count = models.PositiveIntegerField(
        _("Suscriptores de Pago"),
        default=0,
    )
    total_views_count = models.PositiveBigIntegerField(_("Vistas Totales"), default=0)
    views_delta = models.BigIntegerField(_("Variación de Vistas"), default=0)

    class Meta:
        verbose_name = _("Snapshot de Canal")
        verbose_name_plural = _("Snapshots de Canales")
        ordering = ["-snapshot_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["channel", "snapshot_date"],
                name="uq_channel_snapshot_date",
            ),
            models.CheckConstraint(
                condition=Q(followers_count__gte=0) & Q(subscribers_count__gte=0),
                name="chk_snapshot_counts_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.channel} @ {self.snapshot_date}"

    def get_absolute_url(self) -> str:
        return reverse("creators:snapshot_detail", kwargs={"pk": self.pk})
