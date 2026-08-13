from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable
from urllib.parse import urlencode

from poc.geography.models import Point
from .alerts import WeatherAlert
from .core import ProviderProvenance
from .current import CurrentConditions
from .forecast import ExtendedForecastPeriod, HourlyPeriod
from .http_transport import json_get
from . import nws_normalize

JsonTransport = Callable[[str, dict[str, str]], dict[str, Any]]


class NWSProviderError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class NWSPointMetadata:
    point_url: str
    hourly_url: str
    forecast_url: str
    stations_url: str


@dataclass(frozen=True, slots=True)
class NWSForecastBundle:
    current: CurrentConditions
    hourly: tuple[HourlyPeriod, ...]
    extended: tuple[ExtendedForecastPeriod, ...]
    provenance: ProviderProvenance


class NWSClient:
    base_url = "https://api.weather.gov"

    def __init__(self, *, user_agent: str = "Local-Scoop-POC/0.0.3 (https://github.com/Cokkles/Local-Scoop)", transport: JsonTransport = json_get) -> None:
        if not user_agent.strip():
            raise ValueError("NWS requires a non-empty User-Agent")
        self._headers = {"User-Agent": user_agent, "Accept": "application/geo+json"}
        self._transport = transport

    def _get(self, url: str) -> dict[str, Any]:
        try:
            payload = self._transport(url, dict(self._headers))
        except Exception as exc:
            raise NWSProviderError(f"NWS request failed for {url}: {exc}") from exc
        if not isinstance(payload, dict):
            raise NWSProviderError(f"NWS returned a non-object payload for {url}")
        return payload

    def resolve_point(self, point: Point) -> NWSPointMetadata:
        url = f"{self.base_url}/points/{point.latitude:.4f},{point.longitude:.4f}"
        props = self._get(url).get("properties") or {}
        keys = ("forecastHourly", "forecast", "observationStations")
        if not all(props.get(key) for key in keys):
            raise NWSProviderError("NWS point response omitted required links")
        return NWSPointMetadata(url, str(props["forecastHourly"]), str(props["forecast"]), str(props["observationStations"]))

    def fetch_forecast(self, point: Point, retrieved_at: datetime) -> NWSForecastBundle:
        meta = self.resolve_point(point)
        features = self._get(meta.stations_url).get("features") or []
        if not features:
            raise NWSProviderError("NWS returned no observation stations for point")
        station = features[0]
        station_url = str(station.get("id") or "").rstrip("/")
        if not station_url:
            raise NWSProviderError("NWS station result did not include an id URL")
        station_id = str((station.get("properties") or {}).get("stationIdentifier") or station_url.rsplit("/", 1)[-1])
        observation_url = f"{station_url}/observations/latest"
        current = nws_normalize.observation(self._get(observation_url), station_id)
        try:
            hourly = nws_normalize.hourly(self._get(meta.hourly_url))
            extended = nws_normalize.extended(self._get(meta.forecast_url))
        except ValueError as exc:
            raise NWSProviderError(str(exc)) from exc
        endpoints = (meta.point_url, meta.stations_url, observation_url, meta.hourly_url, meta.forecast_url)
        return NWSForecastBundle(current, hourly, extended, ProviderProvenance("nws", retrieved_at, endpoints))

    def fetch_alerts(self, point: Point, retrieved_at: datetime) -> tuple[tuple[WeatherAlert, ...], ProviderProvenance]:
        query = urlencode({"point": f"{point.latitude:.4f},{point.longitude:.4f}"})
        url = f"{self.base_url}/alerts/active?{query}"
        alerts = tuple(nws_normalize.alert(feature) for feature in self._get(url).get("features") or [])
        return alerts, ProviderProvenance("nws-alerts", retrieved_at, (url,))
