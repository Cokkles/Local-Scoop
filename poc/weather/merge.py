from __future__ import annotations

from dataclasses import replace

from .models import CurrentConditions, HourlyPeriod
from .util import coalesce, rounded_hour_key


def merge_current(nws: CurrentConditions, detail: CurrentConditions | None) -> CurrentConditions:
    if detail is None:
        return nws
    source_ids = tuple(dict.fromkeys((*nws.source_ids, *detail.source_ids)))
    return CurrentConditions(
        observed_at=nws.observed_at or detail.observed_at,
        temperature_f=coalesce(nws.temperature_f, detail.temperature_f),
        apparent_temperature_f=detail.apparent_temperature_f,
        relative_humidity_pct=coalesce(nws.relative_humidity_pct, detail.relative_humidity_pct),
        dew_point_f=nws.dew_point_f,
        wind_speed_mph=coalesce(nws.wind_speed_mph, detail.wind_speed_mph),
        wind_gust_mph=coalesce(nws.wind_gust_mph, detail.wind_gust_mph),
        wind_direction_deg=coalesce(nws.wind_direction_deg, detail.wind_direction_deg),
        pressure_hpa=coalesce(nws.pressure_hpa, detail.pressure_hpa),
        visibility_miles=nws.visibility_miles,
        cloud_cover_pct=detail.cloud_cover_pct,
        precipitation_in=detail.precipitation_in,
        description=nws.description,
        icon_url=nws.icon_url,
        station_id=nws.station_id,
        source_ids=source_ids,
    )


def merge_hourly(nws_periods: tuple[HourlyPeriod, ...], detail_periods: tuple[HourlyPeriod, ...] | None) -> tuple[HourlyPeriod, ...]:
    if not detail_periods:
        return nws_periods
    details = {rounded_hour_key(period.start_time): period for period in detail_periods}
    merged: list[HourlyPeriod] = []
    for primary in nws_periods:
        detail = details.get(rounded_hour_key(primary.start_time))
        if detail is None:
            merged.append(primary)
            continue
        source_ids = tuple(dict.fromkeys((*primary.source_ids, *detail.source_ids)))
        merged.append(
            replace(
                primary,
                apparent_temperature_f=detail.apparent_temperature_f,
                relative_humidity_pct=detail.relative_humidity_pct,
                dew_point_f=detail.dew_point_f,
                precipitation_in=detail.precipitation_in,
                rain_in=detail.rain_in,
                showers_in=detail.showers_in,
                cloud_cover_pct=detail.cloud_cover_pct,
                visibility_miles=detail.visibility_miles,
                wind_gust_mph=detail.wind_gust_mph,
                uv_index=detail.uv_index,
                source_ids=source_ids,
            )
        )
    return tuple(merged)
