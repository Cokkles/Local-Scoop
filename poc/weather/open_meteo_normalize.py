from __future__ import annotations

from typing import Any

from .current import CurrentConditions
from .forecast import HourlyPeriod
from .util import parse_datetime


def current(payload: dict[str, Any]) -> CurrentConditions:
    return CurrentConditions(
        observed_at=parse_datetime(payload.get("time")),
        temperature_f=_num(payload.get("temperature_2m")),
        apparent_temperature_f=_num(payload.get("apparent_temperature")),
        relative_humidity_pct=_num(payload.get("relative_humidity_2m")),
        wind_speed_mph=_num(payload.get("wind_speed_10m")),
        wind_gust_mph=_num(payload.get("wind_gusts_10m")),
        wind_direction_deg=_num(payload.get("wind_direction_10m")),
        pressure_hpa=_num(payload.get("pressure_msl")),
        cloud_cover_pct=_num(payload.get("cloud_cover")),
        precipitation_in=_num(payload.get("precipitation")),
        source_ids=("open-meteo",),
    )


def hourly(payload: dict[str, Any]) -> tuple[HourlyPeriod, ...]:
    times = payload.get("time") or []
    if not isinstance(times, list) or not times:
        raise ValueError("Open-Meteo hourly response did not contain time values")

    def value(name: str, index: int) -> float | None:
        values = payload.get(name) or []
        return _num(values[index]) if index < len(values) else None

    periods = []
    for index, raw_time in enumerate(times):
        start = parse_datetime(str(raw_time))
        if start is None:
            continue
        periods.append(HourlyPeriod(
            start_time=start,
            temperature_f=value("temperature_2m", index),
            apparent_temperature_f=value("apparent_temperature", index),
            relative_humidity_pct=value("relative_humidity_2m", index),
            dew_point_f=value("dew_point_2m", index),
            precipitation_probability_pct=value("precipitation_probability", index),
            precipitation_in=value("precipitation", index), rain_in=value("rain", index),
            showers_in=value("showers", index), cloud_cover_pct=value("cloud_cover", index),
            visibility_miles=_meters_to_miles(value("visibility", index)),
            wind_speed_mph=value("wind_speed_10m", index), wind_gust_mph=value("wind_gusts_10m", index),
            wind_direction_deg=value("wind_direction_10m", index), uv_index=value("uv_index", index),
            source_ids=("open-meteo",),
        ))
    return tuple(periods)


def _num(value: Any) -> float | None:
    return None if value is None else float(value)


def _meters_to_miles(value: float | None) -> float | None:
    return None if value is None else value / 1609.344
