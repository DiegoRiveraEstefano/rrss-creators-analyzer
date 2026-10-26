import logging
from decimal import Decimal

from django.db import transaction

from .exceptions import BusinessLogicError
from .models import CompanySettings

logger = logging.getLogger(__name__)


class CompanySettingsService:
    @classmethod
    @transaction.atomic
    def save_settings(  # noqa: PLR0913
        cls,
        *,
        instance: CompanySettings | None = None,
        company_name: str,
        legal_name: str = "",
        tax_id: str = "",
        logo_url: str = "",
        default_currency: str = "USD",
        default_timezone: str = "UTC",
        default_agency_split_pct: Decimal = Decimal("20.00"),
        default_creator_split_pct: Decimal = Decimal("80.00"),
        alert_webhook_url: str = "",
    ) -> CompanySettings:
        if default_agency_split_pct + default_creator_split_pct != Decimal("100.00"):
            msg = (
                "La suma del porcentaje de agencia y creador "
                "debe ser exactamente 100.00%."
            )
            raise BusinessLogicError(msg)

        obj = instance or CompanySettings()
        obj.company_name = company_name
        obj.legal_name = legal_name
        obj.tax_id = tax_id
        obj.logo_url = logo_url
        obj.default_currency = default_currency
        obj.default_timezone = default_timezone
        obj.default_agency_split_pct = default_agency_split_pct
        obj.default_creator_split_pct = default_creator_split_pct
        obj.alert_webhook_url = alert_webhook_url
        obj.save()

        logger.info("company_settings_saved", extra={"settings_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_settings(cls, *, instance: CompanySettings) -> None:
        settings_id = instance.id
        instance.delete()
        logger.info("company_settings_deleted", extra={"settings_id": settings_id})
