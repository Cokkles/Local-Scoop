from __future__ import annotations

from typing import Any

from .forecast import ExtendedForecastPeriod, HourlyPeriod
from .util import nws_temperature, parse_datetime, parse_wind_speed_mph


def hourly(payload: dict[str, Any]) -> tuple[HourlyPeriod, ...]:
    result = []
    for period in (payload.get("properties") or {}).get("periods") or []:
        start = parse_datetime(period.get("startTime"))
        if start is None:
            continue
        pop = (period.get("probabilityOfPrecipitation") or {}).get("value")
        result.append(HourlyPeriod(
            start_time=start,
            temperature_f=nws_temperature(period.get("temperature"), period.get("temperatureUnit")),
            precipitation_probability_pct=float(pop) if pop is not None else None,
            wind_speed_mph=parse_wind_speed_mph(period.get("windSpeed")),
            short_forecast=period.get("shortForecast"), is_daytime=period.get("isDaytime"),
            source_ids=("nws",),
        ))
    if not result:
        raise ValueError("NWS hourly response did not contain usable periods")
    return tuple(result)


def extended(payload: dict[str, Any]) -> tuple[ExtendedForecastPeriod, ...]:
    result = []
    for period in (payload.get("properties") or {}).get("periods") or []:
        start = parse_datetime(period.get("startTime"))
        if start is None:
            continue
        pop = (period.get("probabilityOfPrecipitation") or {}).get("value")
        result.append(ExtendedForecastPeriod(
            name=str(period.get("name") or "Forecast period"), start_time=start,
            end_time=parse_datetime(period.get("endTime")), is_daytime=period.get("isDaytime"),
            temperature_f=nws_temperature(period.get("temperature"), period.get("temperatureUnit")),
            precipitation_probability_pct=float(pop) if pop is not None else None,
            wind_speed_mph=parse_wind_speed_mph(period.get("windSpeed")),
            wind_direction=period.get("windDirection"), short_forecast=period.get("shortForecast"),
            detailed_forecast=period.get("detailedForecast"),
        ))
    if not result:
        raise ValueError("NWS extended forecast response did not contain usable periods")
    return tuple(result)
