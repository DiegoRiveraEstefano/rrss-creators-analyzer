from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.contracts.models import Contract
from rrss_creatos_analyzer.apps.core.choices import PayoutStatus
from rrss_creatos_analyzer.apps.core.models import BaseModel
from rrss_creatos_analyzer.apps.creators.models import Creator


class CreatorPayout(BaseModel):
    creator = models.ForeignKey(
        Creator,
        on_delete=models.CASCADE,
        related_name="payouts",
        verbose_name=_("Creador"),
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payouts",
        verbose_name=_("Contrato Aplicado"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payouts",
        verbose_name=_("Aprobado por"),
    )

    period_year = models.PositiveIntegerField(_("Año del Periodo"))
    period_month = models.PositiveIntegerField(_("Mes del Periodo (1-12)"))
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=PayoutStatus.choices,
        default=PayoutStatus.DRAFT,
        db_index=True,
    )

    gross_stream_revenue = models.DecimalField(
        _("Ingresos Brutos Streams ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    gross_video_revenue = models.DecimalField(
        _("Ingresos Brutos Videos ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    gross_sponsorship_revenue = models.DecimalField(
        _("Ingresos Brutos Patrocinios ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    base_retainer_amount = models.DecimalField(
        _("Retainer Fijo ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    bonuses_amount = models.DecimalField(
        _("Bonos ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    deductions_or_recoupment = models.DecimalField(
        _("Deducciones / Anticipos ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    agency_commission_amount = models.DecimalField(
        _("Comisión Agencia ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    net_creator_payout = models.DecimalField(
        _("Pago Neto al Creador ($)"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    invoice_reference = models.CharField(
        _("Referencia de Factura"),
        max_length=120,
        blank=True,
    )
    paid_at = models.DateTimeField(_("Pagado el"), null=True, blank=True)
    notes = models.TextField(_("Notas"), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Liquidación de Creador")
        verbose_name_plural = _("Liquidaciones de Creadores")
        ordering = ["-period_year", "-period_month"]
        constraints = [
            models.UniqueConstraint(
                fields=["creator", "period_year", "period_month"],
                name="uq_creator_payout_period",
            ),
            models.CheckConstraint(
                condition=Q(period_month__gte=1) & Q(period_month__lte=12),
                name="chk_payout_period_month_valid",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.creator.display_name} - {self.period_year}-{self.period_month:02d}"
        )

    def get_absolute_url(self) -> str:
        return reverse("payouts:payout_detail", kwargs={"pk": self.pk})
