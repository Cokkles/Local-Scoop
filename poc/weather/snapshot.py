from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

from poc.geography.models import Point
from .alerts import WeatherAlert
from .core import FreshnessState, ProviderProvenance
from .current import CurrentConditions
from .forecast import ExtendedForecastPeriod, HourlyPeriod


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    weather_id: str
    region_id: str
    point: Point
    timezone_name: str
    retrieved_at: datetime
    current: CurrentConditions
    hourly: tuple[HourlyPeriod, ...]
    extended: tuple[ExtendedForecastPeriod, ...]
    alerts: tuple[WeatherAlert, ...]
    provenance: tuple[ProviderProvenance, ...]
    forecast_retrieved_at: datetime
    alerts_retrieved_at: datetime
    provider_errors: tuple[str, ...] = field(default_factory=tuple)
    freshness: FreshnessState = FreshnessState.FRESH

    def with_freshness(self, state: FreshnessState) -> "WeatherSnapshot":
        return replace(self, freshness=state)

    def to_contract(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0", "weather_id": self.weather_id, "region_id": self.region_id,
            "location": {"latitude": self.point.latitude, "longitude": self.point.longitude, "timezone": self.timezone_name},
            "retrieved_at": self.retrieved_at.isoformat(), "forecast_retrieved_at": self.forecast_retrieved_at.isoformat(),
            "alerts_retrieved_at": self.alerts_retrieved_at.isoformat(), "freshness": self.freshness.value,
            "current": self.current.to_contract(), "hourly": [p.to_contract() for p in self.hourly],
            "extended": [p.to_contract() for p in self.extended], "alerts": [a.to_contract() for a in self.alerts],
            "provenance": [p.to_contract() for p in self.provenance], "provider_errors": list(self.provider_errors),
        }
