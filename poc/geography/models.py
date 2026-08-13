from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class CoverageMode(StrEnum):
    COUNTY = "county"
    ADJACENT_COUNTIES = "adjacent_counties"
    RADIUS = "radius"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class Point:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")


@dataclass(frozen=True, slots=True)
class CountyRef:
    geoid: str
    name: str
    state: str
    shared_boundary_m: int | None = None

    @property
    def region_id(self) -> str:
        return f"us:county:{self.geoid}"


@dataclass(frozen=True, slots=True)
class GeographyLookup:
    point: Point
    county: CountyRef
    state_fips: str
    state_name: str
    city: str | None = None
    place_geoid: str | None = None


@dataclass(frozen=True, slots=True)
class RegionContext:
    region_id: str
    home_region_id: str
    point: Point
    city: str | None
    county: CountyRef
    state_fips: str
    state_name: str
    timezone: str
    coverage_mode: CoverageMode
    included_regions: tuple[CountyRef, ...]
    excluded_region_ids: tuple[str, ...] = field(default_factory=tuple)
    radius_miles: float | None = None
    geography_source: str = "US Census Bureau"
    adjacency_vintage: str | None = None

    def to_contract(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "region_id": self.region_id,
            "home": {
                "region_id": self.home_region_id,
                "latitude": self.point.latitude,
                "longitude": self.point.longitude,
                "city": self.city or "",
                "county": self.county.name,
                "county_geoid": self.county.geoid,
                "state": self.county.state,
                "state_fips": self.state_fips,
                "timezone": self.timezone,
            },
            "coverage_mode": self.coverage_mode.value,
            "included_regions": [
                {
                    "region_id": county.region_id,
                    "county": county.name,
                    "county_geoid": county.geoid,
                    "state": county.state,
                    "shared_boundary_m": county.shared_boundary_m,
                }
                for county in self.included_regions
            ],
            "excluded_regions": list(self.excluded_region_ids),
            "radius_miles": self.radius_miles,
            "provenance": {
                "geography_source": self.geography_source,
                "adjacency_vintage": self.adjacency_vintage,
            },
        }
