from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class CurrentConditions:
    observed_at: datetime | None = None
    temperature_f: float | None = None
    apparent_temperature_f: float | None = None
    relative_humidity_pct: float | None = None
    dew_point_f: float | None = None
    wind_speed_mph: float | None = None
    wind_gust_mph: float | None = None
    wind_direction_deg: float | None = None
    pressure_hpa: float | None = None
    visibility_miles: float | None = None
    cloud_cover_pct: float | None = None
    precipitation_in: float | None = None
    description: str | None = None
    icon_url: str | None = None
    station_id: str | None = None
    source_ids: tuple[str, ...] = field(default_factory=tuple)

    def to_contract(self) -> dict[str, Any]:
        return {
            "observed_at": self.observed_at.isoformat() if self.observed_at else None,
            "temperature_f": self.temperature_f, "apparent_temperature_f": self.apparent_temperature_f,
            "relative_humidity_pct": self.relative_humidity_pct, "dew_point_f": self.dew_point_f,
            "wind_speed_mph": self.wind_speed_mph, "wind_gust_mph": self.wind_gust_mph,
            "wind_direction_deg": self.wind_direction_deg, "pressure_hpa": self.pressure_hpa,
            "visibility_miles": self.visibility_miles, "cloud_cover_pct": self.cloud_cover_pct,
            "precipitation_in": self.precipitation_in, "description": self.description,
            "icon_url": self.icon_url, "station_id": self.station_id, "source_ids": list(self.source_ids),
        }
