from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from rrss_creatos_analyzer.apps.core.choices import CampaignStatus
from rrss_creatos_analyzer.apps.core.choices import DeliverableStatus
from rrss_creatos_analyzer.apps.core.choices import DeliverableType
from rrss_creatos_analyzer.apps.core.choices import PlatformType
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Creator
from rrss_creatos_analyzer.apps.streams.models import StreamingSession
from rrss_creatos_analyzer.apps.videos.models import VideoPublication


class SponsorCampaign(BaseModel):
    account_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_campaigns",
        verbose_name=_("Account Manager"),
    )
    brand_name = models.CharField(_("Marca / Sponsor"), max_length=150)
    campaign_name = models.CharField(_("Nombre de Campaña"), max_length=200)
    campaign_code = models.CharField(_("Código de Campaña"), max_length=60, unique=True)
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=CampaignStatus.choices,
        default=CampaignStatus.ACTIVE,
        db_index=True,
    )
    start_date = models.DateField(_("Fecha de Inicio"))
    end_date = models.DateField(_("Fecha de Fin"), null=True, blank=True)

    total_budget = models.DecimalField(
        _("Presupuesto Total ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    agency_fee_amount = models.DecimalField(
        _("Comisión Agencia ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    creator_pool_amount = models.DecimalField(
        _("Fondo Creadores ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    target_views_or_impressions = models.PositiveBigIntegerField(
        _("Meta de Vistas/Impresiones"),
        default=0,
    )

    brief_url = models.URLField(_("URL del Brief"), max_length=500, blank=True)
    notes = models.TextField(_("Notas"), blank=True)

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Campaña de Patrocinio")
        verbose_name_plural = _("Campañas de Patrocinio")
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_budget__gte=0) & Q(agency_fee_amount__gte=0),
                name="chk_campaign_budget_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.brand_name} - {self.campaign_name} ({self.campaign_code})"

    def get_absolute_url(self) -> str:
        return reverse("campaigns:campaign_detail", kwargs={"pk": self.pk})


class CampaignDeliverable(BaseModel):
    campaign = models.ForeignKey(
        SponsorCampaign,
        on_delete=models.CASCADE,
        related_name="deliverables",
        verbose_name=_("Campaña"),
    )
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="campaign_deliverables",
        verbose_name=_("Creador"),
    )
    linked_session = models.ForeignKey(
        StreamingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaign_deliverables",
        verbose_name=_("Sesión Vinculada"),
    )
    linked_publication = models.ForeignKey(
        VideoPublication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaign_deliverables",
        verbose_name=_("Publicación Vinculada"),
    )

    deliverable_type = models.CharField(
        _("Tipo de Entregable"),
        max_length=30,
        choices=DeliverableType.choices,
        default=DeliverableType.SPONSORED_STREAM,
    )
    platform = models.CharField(
        _("Plataforma"),
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.TWITCH,
    )
    title = models.CharField(_("Título / Descripción del Entregable"), max_length=255)
    due_date = models.DateField(_("Fecha de Entrega"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completado el"), null=True, blank=True)
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=DeliverableStatus.choices,
        default=DeliverableStatus.PENDING,
        db_index=True,
    )

    agreed_creator_payout = models.DecimalField(
        _("Pago Acordado al Creador ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    tracking_link = models.URLField(_("Link de Tracking"), max_length=500, blank=True)
    promo_code = models.CharField(_("Código Promocional"), max_length=60, blank=True)
    conversions_count = models.PositiveIntegerField(
        _("Conversiones / Clics"),
        default=0,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Entregable de Campaña")
        verbose_name_plural = _("Entregables de Campaña")
        ordering = ["-due_date", "-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.title} - {self.creator.display_name} ({self.campaign.brand_name})"
        )

    def get_absolute_url(self) -> str:
        return reverse("campaigns:deliverable_detail", kwargs={"pk": self.pk})
