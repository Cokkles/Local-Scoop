from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable
from urllib.parse import urlencode

from poc.geography.models import Point
from . import open_meteo_normalize
from .core import ProviderProvenance
from .current import CurrentConditions
from .forecast import HourlyPeriod
from .http_transport import json_get

JsonTransport = Callable[[str, dict[str, str]], dict[str, Any]]


class OpenMeteoProviderError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class OpenMeteoBundle:
    current: CurrentConditions
    hourly: tuple[HourlyPeriod, ...]
    provenance: ProviderProvenance


class OpenMeteoClient:
    base_url = "https://api.open-meteo.com/v1/forecast"
    CURRENT = ("temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "weather_code", "cloud_cover", "pressure_msl", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m")
    HOURLY = ("temperature_2m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "showers", "weather_code", "cloud_cover", "visibility", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "uv_index")

    def __init__(self, *, transport: JsonTransport = json_get) -> None:
        self._transport = transport

    def build_url(self, point: Point, timezone_name: str, forecast_days: int = 7) -> str:
        if not 1 <= forecast_days <= 16:
            raise ValueError("Open-Meteo forecast_days must be between 1 and 16")
        query = urlencode({
            "latitude": f"{point.latitude:.4f}", "longitude": f"{point.longitude:.4f}",
            "current": ",".join(self.CURRENT), "hourly": ",".join(self.HOURLY),
            "temperature_unit": "fahrenheit", "wind_speed_unit": "mph", "precipitation_unit": "inch",
            "timezone": timezone_name, "forecast_days": str(forecast_days),
        })
        return f"{self.base_url}?{query}"

    def fetch(self, point: Point, timezone_name: str, retrieved_at: datetime, forecast_days: int = 7) -> OpenMeteoBundle:
        url = self.build_url(point, timezone_name, forecast_days)
        try:
            payload = self._transport(url, {"User-Agent": "Local-Scoop-POC/0.0.3"})
        except Exception as exc:
            raise OpenMeteoProviderError(f"Open-Meteo request failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise OpenMeteoProviderError("Open-Meteo returned a non-object payload")
        try:
            current = open_meteo_normalize.current(payload.get("current") or {})
            hourly = open_meteo_normalize.hourly(payload.get("hourly") or {})
        except ValueError as exc:
            raise OpenMeteoProviderError(str(exc)) from exc
        return OpenMeteoBundle(current, hourly, ProviderProvenance("open-meteo", retrieved_at, (url,)))
