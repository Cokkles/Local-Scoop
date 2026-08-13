from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Callable

from poc.geography.models import Point
from .cache import MemoryWeatherCache, cache_key
from .merge import merge_current, merge_hourly
from .models import CachePolicy, FreshnessState, WeatherSnapshot, utc_now
from .nws import NWSClient
from .open_meteo import OpenMeteoClient

Clock = Callable[[], datetime]


class WeatherUnavailableError(RuntimeError):
    pass


class WeatherService:
    def __init__(
        self,
        *,
        nws: NWSClient,
        detail: OpenMeteoClient | None = None,
        cache: MemoryWeatherCache | None = None,
        policy: CachePolicy | None = None,
        clock: Clock = utc_now,
    ) -> None:
        self.nws = nws
        self.detail = detail
        self.cache = cache or MemoryWeatherCache()
        self.policy = policy or CachePolicy()
        self.clock = clock

    def get(self, *, region_id: str, point: Point, timezone_name: str, force: bool = False) -> WeatherSnapshot:
        now = self.clock()
        key = cache_key(region_id)
        cached = self.cache.get(key)
        forecast_fresh = cached is not None and now - cached.forecast_retrieved_at <= self.policy.forecast_ttl
        alerts_fresh = cached is not None and now - cached.alerts_retrieved_at <= self.policy.alerts_ttl
        if cached is not None and forecast_fresh and alerts_fresh and not force:
            return cached.with_freshness(FreshnessState.FRESH)

        errors: list[str] = []
        forecast_retrieved_at = cached.forecast_retrieved_at if cached else now
        alerts_retrieved_at = cached.alerts_retrieved_at if cached else now
        current = cached.current if cached else None
        hourly = cached.hourly if cached else ()
        extended = cached.extended if cached else ()
        alerts = cached.alerts if cached else ()
        provenance = list(cached.provenance) if cached else []

        if force or not forecast_fresh:
            try:
                nws_bundle = self.nws.fetch_forecast(point, now)
                detail_bundle = None
                if self.detail is not None:
                    try:
                        detail_bundle = self.detail.fetch(point, timezone_name, now)
                    except Exception as exc:
                        errors.append(str(exc))
                current = merge_current(nws_bundle.current, detail_bundle.current if detail_bundle else None)
                hourly = merge_hourly(nws_bundle.hourly, detail_bundle.hourly if detail_bundle else None)
                extended = nws_bundle.extended
                forecast_retrieved_at = now
                provenance = _replace_provider(provenance, nws_bundle.provenance)
                if detail_bundle:
                    provenance = _replace_provider(provenance, detail_bundle.provenance)
            except Exception as exc:
                errors.append(str(exc))
                if cached is None or now - cached.forecast_retrieved_at > self.policy.expire_after:
                    raise WeatherUnavailableError("authoritative NWS forecast unavailable and no usable cached snapshot exists") from exc

        if force or not alerts_fresh:
            try:
                alerts, alert_provenance = self.nws.fetch_alerts(point, now)
                alerts_retrieved_at = now
                provenance = _replace_provider(provenance, alert_provenance)
            except Exception as exc:
                errors.append(str(exc))
                if cached is None:
                    alerts = ()

        if current is None or not hourly or not extended:
            raise WeatherUnavailableError("weather provider did not produce usable current/hourly data")

        if now - forecast_retrieved_at > self.policy.expire_after:
            freshness = FreshnessState.EXPIRED
        elif (
            now - forecast_retrieved_at > self.policy.forecast_ttl
            or now - alerts_retrieved_at > self.policy.alerts_ttl
        ):
            freshness = FreshnessState.STALE
        else:
            freshness = FreshnessState.FRESH
        weather_id = _weather_id(region_id, forecast_retrieved_at, alerts_retrieved_at)
        snapshot = WeatherSnapshot(
            weather_id=weather_id,
            region_id=region_id,
            point=point,
            timezone_name=timezone_name,
            retrieved_at=now,
            current=current,
            hourly=tuple(hourly),
            extended=tuple(extended),
            alerts=tuple(alerts),
            provenance=tuple(provenance),
            forecast_retrieved_at=forecast_retrieved_at,
            alerts_retrieved_at=alerts_retrieved_at,
            provider_errors=tuple(errors),
            freshness=freshness,
        )
        self.cache.put(key, snapshot)
        return snapshot


def _replace_provider(items, new_item):
    return [item for item in items if item.source_id != new_item.source_id] + [new_item]


def _weather_id(region_id: str, forecast_at: datetime, alerts_at: datetime) -> str:
    raw = f"{region_id}|{forecast_at.isoformat()}|{alerts_at.isoformat()}".encode()
    return "wx1:" + hashlib.sha256(raw).hexdigest()[:24]
