from __future__ import annotations

from typing import Any

from .alerts import WeatherAlert
from .util import parse_datetime


def normalize(feature: dict[str, Any]) -> WeatherAlert:
    props = feature.get("properties") or {}
    alert_id = str(feature.get("id") or props.get("id") or props.get("@id") or "")
    return WeatherAlert(
        alert_id=alert_id,
        event=str(props.get("event") or "Weather Alert"),
        headline=props.get("headline"),
        severity=props.get("severity"),
        urgency=props.get("urgency"),
        certainty=props.get("certainty"),
        status=props.get("status"),
        area_description=props.get("areaDesc"),
        effective_at=parse_datetime(props.get("effective")),
        expires_at=parse_datetime(props.get("expires")),
        sender_name=props.get("senderName"),
        source_url=alert_id or None,
    )
