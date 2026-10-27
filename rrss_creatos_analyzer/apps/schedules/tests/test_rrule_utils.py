from datetime import date

import pytest
from django.core.exceptions import ValidationError

from rrss_creatos_analyzer.apps.schedules.rrule_utils import build_rrule_from_components
from rrss_creatos_analyzer.apps.schedules.rrule_utils import parse_rrule_components
from rrss_creatos_analyzer.apps.schedules.rrule_utils import rrule_to_human
from rrss_creatos_analyzer.apps.schedules.rrule_utils import validate_rrule


class TestRRuleUtils:
    def test_validate_valid_rrule(self):
        validate_rrule("FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1")
        validate_rrule("RRULE:FREQ=DAILY;INTERVAL=2")
        validate_rrule("FREQ=MONTHLY;BYMONTHDAY=15")

    def test_validate_invalid_rrule_raises_error(self):
        with pytest.raises(ValidationError, match="no puede estar vacía"):
            validate_rrule("")

        with pytest.raises(ValidationError, match="inválida"):
            validate_rrule("NOT_A_VALID_RRULE_FORMAT_123")

    def test_parse_rrule_components(self):
        res = parse_rrule_components("FREQ=WEEKLY;INTERVAL=2;BYDAY=TU,TH")
        assert res["freq"] == "WEEKLY"
        assert res["interval"] == 2  # noqa: PLR2004
        assert res["byday"] == ["TU", "TH"]

    def test_build_rrule_from_components(self):
        rule = build_rrule_from_components(
            freq="WEEKLY",
            interval=1,
            byday=["MO", "WE", "FR"],
        )
        assert rule == "FREQ=WEEKLY;BYDAY=MO,WE,FR"

        rule_until = build_rrule_from_components(
            freq="DAILY",
            interval=3,
            until=date(2026, 12, 31),
        )
        assert rule_until == "FREQ=DAILY;INTERVAL=3;UNTIL=20261231"

    def test_rrule_to_human_spanish(self):
        h1 = rrule_to_human("FREQ=DAILY;INTERVAL=1")
        assert h1 == "Todos los días"

        h2 = rrule_to_human("FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1")
        assert "Cada semana los Lunes, Miércoles y Viernes" in h2

        h3 = rrule_to_human("FREQ=WEEKLY;BYDAY=SA,SU;INTERVAL=2")
        assert "Cada 2 semanas los Sábados y Domingos" in h3
