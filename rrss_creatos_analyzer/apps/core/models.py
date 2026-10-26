from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from rrss_creatos_analyzer.apps.core.base_models import ActiveBaseModel
from rrss_creatos_analyzer.apps.core.base_models import ActiveManager
from rrss_creatos_analyzer.apps.core.base_models import ActiveModelMixin
from rrss_creatos_analyzer.apps.core.base_models import ActiveQuerySet
from rrss_creatos_analyzer.apps.core.base_models import ArchivableManager
from rrss_creatos_analyzer.apps.core.base_models import ArchivableModelMixin
from rrss_creatos_analyzer.apps.core.base_models import ArchivableQuerySet
from rrss_creatos_analyzer.apps.core.base_models import BaseModel
from rrss_creatos_analyzer.apps.core.base_models import DateRangeModelMixin
from rrss_creatos_analyzer.apps.core.base_models import MetadataModelMixin
from rrss_creatos_analyzer.apps.core.base_models import MonetaryModelMixin
from rrss_creatos_analyzer.apps.core.base_models import NameDescriptionModelMixin
from rrss_creatos_analyzer.apps.core.base_models import NameSlugDescriptionModel
from rrss_creatos_analyzer.apps.core.base_models import OnlyActiveManager
from rrss_creatos_analyzer.apps.core.base_models import OrderableModelMixin
from rrss_creatos_analyzer.apps.core.base_models import SluggedModelMixin
from rrss_creatos_analyzer.apps.core.base_models import SoftDeletableModelMixin
from rrss_creatos_analyzer.apps.core.base_models import SoftDeleteBaseModel
from rrss_creatos_analyzer.apps.core.base_models import SoftDeleteManager
from rrss_creatos_analyzer.apps.core.base_models import SoftDeleteQuerySet
from rrss_creatos_analyzer.apps.core.base_models import StandardModel
from rrss_creatos_analyzer.apps.core.base_models import StandardUUIDModel
from rrss_creatos_analyzer.apps.core.base_models import TitleDescriptionModelMixin
from rrss_creatos_analyzer.apps.core.base_models import TitleSlugDescriptionModel
from rrss_creatos_analyzer.apps.core.base_models import UserTrackingModelMixin
from rrss_creatos_analyzer.apps.core.base_models import UUIDBaseModel
from rrss_creatos_analyzer.apps.core.base_models import UUIDModelMixin
from rrss_creatos_analyzer.apps.core.base_models import UUIDPrimaryKeyModelMixin


@auditlog.register()
class CompanySettings(BaseModel):
    """Singleton model for Single-Tenant / Single-Company configuration."""

    company_name = models.CharField(
        _("Nombre de la Compañía"),
        max_length=200,
        default="My Creator Agency",
    )
    legal_name = models.CharField(_("Razón Social"), max_length=255, blank=True)
    tax_id = models.CharField(
        _("Identificación Fiscal (RUT/NIT/Tax ID)"),
        max_length=100,
        blank=True,
    )
    logo_url = models.URLField(_("URL del Logo"), max_length=500, blank=True)
    default_currency = models.CharField(_("Moneda Base"), max_length=3, default="USD")
    default_timezone = models.CharField(_("Zona Horaria"), max_length=64, default="UTC")
    default_agency_split_pct = models.DecimalField(
        _("Porcentaje Agencia por Defecto (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
    )
    default_creator_split_pct = models.DecimalField(
        _("Porcentaje Creador por Defecto (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("80.00"),
    )
    alert_webhook_url = models.URLField(
        _("Webhook de Alertas"),
        max_length=500,
        blank=True,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Configuración de Compañía")
        verbose_name_plural = _("Configuraciones de Compañía")
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(default_agency_split_pct__gte=0)
                    & Q(default_creator_split_pct__gte=0)
                    & Q(
                        default_agency_split_pct__exact=Decimal("100.00")
                        - F("default_creator_split_pct"),
                    )
                ),
                name="chk_company_splits_sum_100",
            ),
        ]

    def __str__(self) -> str:
        return self.company_name

    def get_absolute_url(self) -> str:
        return reverse("core:settings_detail", kwargs={"pk": self.pk})


__all__ = [
    "ActiveBaseModel",
    "ActiveManager",
    "ActiveModelMixin",
    "ActiveQuerySet",
    "ArchivableManager",
    "ArchivableModelMixin",
    "ArchivableQuerySet",
    "BaseModel",
    "CompanySettings",
    "DateRangeModelMixin",
    "MetadataModelMixin",
    "MonetaryModelMixin",
    "NameDescriptionModelMixin",
    "NameSlugDescriptionModel",
    "OnlyActiveManager",
    "OrderableModelMixin",
    "SluggedModelMixin",
    "SoftDeletableModelMixin",
    "SoftDeleteBaseModel",
    "SoftDeleteManager",
    "SoftDeleteQuerySet",
    "StandardModel",
    "StandardUUIDModel",
    "TitleDescriptionModelMixin",
    "TitleSlugDescriptionModel",
    "UUIDBaseModel",
    "UUIDModelMixin",
    "UUIDPrimaryKeyModelMixin",
    "UserTrackingModelMixin",
]
