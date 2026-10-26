import logging
from decimal import Decimal

from django.db import transaction

from rrss_creatos_analyzer.apps.core.exceptions import BusinessLogicError

from .models import Contract

logger = logging.getLogger(__name__)


class ContractService:
    @classmethod
    @transaction.atomic
    def save_contract(cls, *, instance: Contract | None = None, **data) -> Contract:
        stream_total = data.get(
            "stream_creator_split_pct",
            Decimal("80.00"),
        ) + data.get("stream_agency_split_pct", Decimal("20.00"))
        if stream_total != Decimal("100.00"):
            msg = "El split de streams entre creador y agencia debe sumar 100.00%."
            raise BusinessLogicError(msg)

        contract = instance or Contract()
        for field, value in data.items():
            setattr(contract, field, value)
        contract.save()
        logger.info(
            "contract_saved",
            extra={"contract_id": contract.id, "code": contract.contract_code},
        )
        return contract

    @classmethod
    @transaction.atomic
    def delete_contract(cls, *, instance: Contract) -> None:
        contract_id = instance.id
        instance.delete()
        logger.info("contract_deleted", extra={"contract_id": contract_id})
