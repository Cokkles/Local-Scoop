from __future__ import annotations

from typing import Any

from .current import CurrentConditions
from .util import parse_datetime, qv_value


def normalize(payload: dict[str, Any], station_id: str) -> CurrentConditions:
    props = payload.get("properties") or {}
    return CurrentConditions(
        observed_at=parse_datetime(props.get("timestamp")),
        temperature_f=qv_value(props.get("temperature"), target="fahrenheit"),
        relative_humidity_pct=qv_value(props.get("relativeHumidity")),
        dew_point_f=qv_value(props.get("dewpoint"), target="fahrenheit"),
        wind_speed_mph=qv_value(props.get("windSpeed"), target="mph"),
        wind_gust_mph=qv_value(props.get("windGust"), target="mph"),
        wind_direction_deg=qv_value(props.get("windDirection")),
        pressure_hpa=qv_value(props.get("barometricPressure"), target="hpa"),
        visibility_miles=qv_value(props.get("visibility"), target="miles"),
        description=props.get("textDescription"), icon_url=props.get("icon"),
        station_id=station_id, source_ids=("nws",),
    )
