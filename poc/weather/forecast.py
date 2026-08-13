from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class HourlyPeriod:
    start_time: datetime
    temperature_f: float | None = None
    apparent_temperature_f: float | None = None
    relative_humidity_pct: float | None = None
    dew_point_f: float | None = None
    precipitation_probability_pct: float | None = None
    precipitation_in: float | None = None
    rain_in: float | None = None
    showers_in: float | None = None
    cloud_cover_pct: float | None = None
    visibility_miles: float | None = None
    wind_speed_mph: float | None = None
    wind_gust_mph: float | None = None
    wind_direction_deg: float | None = None
    uv_index: float | None = None
    short_forecast: str | None = None
    is_daytime: bool | None = None
    source_ids: tuple[str, ...] = field(default_factory=tuple)

    def to_contract(self) -> dict[str, Any]:
        data = {field: getattr(self, field) for field in (
            "temperature_f", "apparent_temperature_f", "relative_humidity_pct", "dew_point_f",
            "precipitation_probability_pct", "precipitation_in", "rain_in", "showers_in",
            "cloud_cover_pct", "visibility_miles", "wind_speed_mph", "wind_gust_mph",
            "wind_direction_deg", "uv_index", "short_forecast", "is_daytime")}
        return data | {"start_time": self.start_time.isoformat(), "source_ids": list(self.source_ids)}


@dataclass(frozen=True, slots=True)
class ExtendedForecastPeriod:
    name: str
    start_time: datetime
    end_time: datetime | None = None
    is_daytime: bool | None = None
    temperature_f: float | None = None
    precipitation_probability_pct: float | None = None
    wind_speed_mph: float | None = None
    wind_direction: str | None = None
    short_forecast: str | None = None
    detailed_forecast: str | None = None
    source_ids: tuple[str, ...] = ("nws",)

    def to_contract(self) -> dict[str, Any]:
        return {
            "name": self.name, "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None, "is_daytime": self.is_daytime,
            "temperature_f": self.temperature_f, "precipitation_probability_pct": self.precipitation_probability_pct,
            "wind_speed_mph": self.wind_speed_mph, "wind_direction": self.wind_direction,
            "short_forecast": self.short_forecast, "detailed_forecast": self.detailed_forecast,
            "source_ids": list(self.source_ids),
        }
