from decimal import Decimal

from django.db import models
from django.db.models import F
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.choices import ContractStatus
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Creator


class Contract(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name=_("Creador"),
    )
    contract_code = models.CharField(
        _("Código de Contrato"),
        max_length=60,
        unique=True,
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.ACTIVE,
        db_index=True,
    )
    start_date = models.DateField(_("Fecha de Inicio"))
    end_date = models.DateField(_("Fecha de Término"), null=True, blank=True)
    auto_renew = models.BooleanField(_("Renovación Automática"), default=False)

    base_monthly_retainer = models.DecimalField(
        _("Retainer Mensual Fijo ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    stream_creator_split_pct = models.DecimalField(
        _("Split Creador Streams (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("80.00"),
    )
    stream_agency_split_pct = models.DecimalField(
        _("Split Agencia Streams (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
    )
    video_creator_split_pct = models.DecimalField(
        _("Split Creador Videos (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("70.00"),
    )
    video_agency_split_pct = models.DecimalField(
        _("Split Agencia Videos (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("30.00"),
    )
    sponsorship_creator_split_pct = models.DecimalField(
        _("Split Creador Patrocinios (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("75.00"),
    )
    sponsorship_agency_split_pct = models.DecimalField(
        _("Split Agencia Patrocinios (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
    )

    min_monthly_stream_hours = models.DecimalField(
        _("Cuota Mínima Horas Stream/Mes"),
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    min_monthly_videos = models.PositiveIntegerField(
        _("Cuota Mínima Videos/Mes"),
        default=0,
    )
    min_monthly_shorts = models.PositiveIntegerField(
        _("Cuota Mínima Shorts/Mes"),
        default=0,
    )

    document_url = models.URLField(
        _("URL Documento Firmado"),
        max_length=500,
        blank=True,
    )
    notes = models.TextField(_("Notas Contractuales"), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Contrato")
        verbose_name_plural = _("Contratos")
        ordering = ["-start_date"]
        permissions = [
            ("manage_contracts", _("Puede gestionar contratos y revenue splits")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(base_monthly_retainer__gte=0)
                & Q(min_monthly_stream_hours__gte=0),
                name="chk_contract_quotas_positive",
            ),
            models.CheckConstraint(
                condition=Q(
                    stream_agency_split_pct__exact=Decimal("100.00")
                    - F("stream_creator_split_pct"),
                ),
                name="chk_contract_stream_split_100",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.contract_code} ({self.creator.display_name})"

    def get_absolute_url(self) -> str:
        return reverse("contracts:contract_detail", kwargs={"pk": self.pk})
