from __future__ import annotations

from datetime import datetime
import math
import re
from typing import Any


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def c_to_f(value: float | None) -> float | None:
    return None if value is None else value * 9 / 5 + 32


def ms_to_mph(value: float | None) -> float | None:
    return None if value is None else value * 2.2369362921


def m_to_miles(value: float | None) -> float | None:
    return None if value is None else value / 1609.344


def qv_value(node: Any, *, target: str | None = None) -> float | None:
    if not isinstance(node, dict):
        return None
    value = node.get("value")
    if value is None:
        return None
    value = float(value)
    unit = str(node.get("unitCode") or "")
    if target == "fahrenheit" and unit.endswith(":degC"):
        return c_to_f(value)
    if target == "mph" and unit.endswith(":m_s-1"):
        return ms_to_mph(value)
    if target == "miles" and unit.endswith(":m"):
        return m_to_miles(value)
    if target == "hpa" and unit.endswith(":Pa"):
        return value / 100
    return value


def nws_temperature(value: float | int | None, unit: str | None) -> float | None:
    if value is None:
        return None
    numeric = float(value)
    if str(unit).upper() == "C":
        return c_to_f(numeric)
    return numeric


def parse_wind_speed_mph(value: str | None) -> float | None:
    if not value:
        return None
    numbers = [float(item) for item in re.findall(r"\d+(?:\.\d+)?", value)]
    if not numbers:
        return None
    if len(numbers) == 1:
        return numbers[0]
    return sum(numbers[:2]) / 2


def rounded_hour_key(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H")


def coalesce(primary: float | None, fallback: float | None) -> float | None:
    return primary if primary is not None and not math.isnan(primary) else fallback
