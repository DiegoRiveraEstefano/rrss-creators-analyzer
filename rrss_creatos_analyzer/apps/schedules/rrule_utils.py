from contextlib import suppress
from datetime import UTC
from datetime import date
from datetime import datetime

from dateutil.rrule import DAILY
from dateutil.rrule import MONTHLY
from dateutil.rrule import WEEKLY
from dateutil.rrule import rrulestr
from django.core.exceptions import ValidationError

DAY_NAMES_ES = {
    "MO": "Lunes",
    "TU": "Martes",
    "WE": "Miércoles",
    "TH": "Jueves",
    "FR": "Viernes",
    "SA": "Sábados",
    "SU": "Domingos",
}

FREQ_MAP = {
    "DAILY": DAILY,
    "WEEKLY": WEEKLY,
    "MONTHLY": MONTHLY,
}

FREQ_NAMES_ES = {
    "DAILY": "día",
    "WEEKLY": "semana",
    "MONTHLY": "mes",
}


def validate_rrule(rrule_str: str) -> None:
    """Valida que una cadena cumpla la especificación RFC 5545 para RRULE."""
    if not rrule_str or not rrule_str.strip():
        msg = "La regla de recurrencia (RRULE) no puede estar vacía."
        raise ValidationError(msg)

    cleaned = rrule_str.strip()
    test_str = cleaned if cleaned.upper().startswith("RRULE:") else f"RRULE:{cleaned}"

    try:
        rrulestr(test_str, dtstart=datetime(2026, 1, 1, 0, 0, tzinfo=UTC))
    except Exception as exc:
        msg = f"Regla de recurrencia (RRULE) inválida: {exc}"
        raise ValidationError(msg) from exc


def _parse_part(key: str, value: str, components: dict) -> None:
    if key == "FREQ":
        components["freq"] = value.upper()
    elif key == "INTERVAL":
        with suppress(ValueError):
            components["interval"] = max(1, int(value))
    elif key == "BYDAY":
        components["byday"] = [d.upper() for d in value.split(",") if d.strip()]
    elif key == "COUNT":
        with suppress(ValueError):
            components["count"] = int(value)
    elif key == "UNTIL":
        components["until"] = value


def parse_rrule_components(rrule_str: str) -> dict:
    """Extrae componentes principales de una RRULE para sincronizar con la UI."""
    cleaned = rrule_str.strip()
    if cleaned.upper().startswith("RRULE:"):
        cleaned = cleaned[6:]

    components: dict = {
        "freq": "WEEKLY",
        "interval": 1,
        "byday": [],
        "count": None,
        "until": None,
    }

    for part in cleaned.split(";"):
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        _parse_part(key.upper().strip(), value.strip(), components)

    return components


def build_rrule_from_components(
    freq: str = "WEEKLY",
    interval: int = 1,
    byday: list[str] | None = None,
    count: int | None = None,
    until: date | None = None,
) -> str:
    """Construye una cadena RRULE RFC 5545 a partir de componentes visuales."""
    freq = freq.upper()
    if freq not in ("DAILY", "WEEKLY", "MONTHLY"):
        freq = "WEEKLY"

    interval = max(1, int(interval))
    parts = [f"FREQ={freq}"]

    if interval > 1:
        parts.append(f"INTERVAL={interval}")

    if freq == "WEEKLY" and byday:
        valid_days = [d.upper() for d in byday if d.upper() in DAY_NAMES_ES]
        if valid_days:
            parts.append(f"BYDAY={','.join(valid_days)}")

    if count and count > 0:
        parts.append(f"COUNT={count}")
    elif until:
        until_str = until.strftime("%Y%m%d")
        parts.append(f"UNTIL={until_str}")

    return ";".join(parts)


def _format_weekly_human(interval: int, byday: list[str]) -> str:
    base = "Cada semana" if interval == 1 else f"Cada {interval} semanas"
    if not byday:
        return base

    day_labels = [DAY_NAMES_ES.get(d, d) for d in byday]
    if len(day_labels) == 1:
        return f"{base} los {day_labels[0]}"
    if len(day_labels) == 2:  # noqa: PLR2004
        return f"{base} los {day_labels[0]} y {day_labels[1]}"
    return f"{base} los {', '.join(day_labels[:-1])} y {day_labels[-1]}"


def rrule_to_human(rrule_str: str) -> str:
    """Convierte una cadena RRULE a texto en lenguaje natural en español."""
    try:
        comp = parse_rrule_components(rrule_str)
    except Exception:  # noqa: BLE001
        return rrule_str

    freq = comp.get("freq", "WEEKLY")
    interval = comp.get("interval", 1)
    byday = comp.get("byday", [])

    if freq == "DAILY":
        base = "Todos los días" if interval == 1 else f"Cada {interval} días"
    elif freq == "WEEKLY":
        base = _format_weekly_human(interval, byday)
    elif freq == "MONTHLY":
        base = "Cada mes" if interval == 1 else f"Cada {interval} meses"
    else:
        base = f"Recurrencia {freq}"

    if comp.get("count"):
        base += f" ({comp['count']} repeticiones)"
    elif comp.get("until"):
        base += f" (hasta {comp['until']})"

    return base
