from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from typing import Protocol

from .adjacency import CountyAdjacencyIndex
from .models import CoverageMode, CountyRef, GeographyLookup, Point, RegionContext


class Geocoder(Protocol):
    def lookup(self, point: Point) -> GeographyLookup: ...


class TimezoneResolver(Protocol):
    def timezone_for(self, lookup: GeographyLookup) -> str: ...


class NorthCarolinaTimezoneResolver:
    """Bounded POC resolver. Phase 0.2 targets the Raleigh/Wake market only."""

    def timezone_for(self, lookup: GeographyLookup) -> str:
        if lookup.state_fips != "37":
            raise ValueError("Phase 0.2 timezone resolver only supports North Carolina")
        return "America/New_York"


class GeographyService:
    def __init__(
        self,
        *,
        geocoder: Geocoder,
        adjacency: CountyAdjacencyIndex,
        timezone_resolver: TimezoneResolver | None = None,
    ) -> None:
        self.geocoder = geocoder
        self.adjacency = adjacency
        self.timezone_resolver = timezone_resolver or NorthCarolinaTimezoneResolver()

    def build_region(
        self,
        point: Point,
        *,
        coverage_mode: CoverageMode = CoverageMode.ADJACENT_COUNTIES,
        radius_miles: float | None = None,
        include_counties: Iterable[CountyRef] = (),
        exclude_region_ids: Iterable[str] = (),
    ) -> RegionContext:
        lookup = self.geocoder.lookup(point)
        timezone = self.timezone_resolver.timezone_for(lookup)
        excluded = tuple(sorted(set(exclude_region_ids)))

        counties: dict[str, CountyRef] = {lookup.county.geoid: lookup.county}
        if coverage_mode is CoverageMode.ADJACENT_COUNTIES:
            counties.update({x.geoid: x for x in self.adjacency.neighbors(lookup.county.geoid)})
        elif coverage_mode is CoverageMode.CUSTOM:
            counties.update({x.geoid: x for x in include_counties})
        elif coverage_mode is CoverageMode.RADIUS:
            if radius_miles is None or radius_miles <= 0:
                raise ValueError("radius coverage requires radius_miles > 0")
        elif coverage_mode is not CoverageMode.COUNTY:
            raise ValueError(f"unsupported coverage mode: {coverage_mode}")

        included = tuple(
            county
            for county in sorted(counties.values(), key=lambda x: x.geoid)
            if county.region_id not in excluded
        )
        if lookup.county.region_id in excluded:
            raise ValueError("home county cannot be excluded")

        region_id = deterministic_region_id(
            home_county_geoid=lookup.county.geoid,
            coverage_mode=coverage_mode,
            included_geoids=(x.geoid for x in included),
            excluded_region_ids=excluded,
            radius_miles=radius_miles,
        )
        return RegionContext(
            region_id=region_id,
            home_region_id=lookup.county.region_id,
            point=point,
            city=lookup.city,
            county=lookup.county,
            state_fips=lookup.state_fips,
            state_name=lookup.state_name,
            timezone=timezone,
            coverage_mode=coverage_mode,
            included_regions=included,
            excluded_region_ids=excluded,
            radius_miles=radius_miles,
            adjacency_vintage=self.adjacency.vintage,
        )


def deterministic_region_id(
    *,
    home_county_geoid: str,
    coverage_mode: CoverageMode,
    included_geoids: Iterable[str],
    excluded_region_ids: Iterable[str],
    radius_miles: float | None,
) -> str:
    canonical = {
        "version": 1,
        "home_county_geoid": home_county_geoid,
        "coverage_mode": coverage_mode.value,
        "included_geoids": sorted(set(included_geoids)),
        "excluded_region_ids": sorted(set(excluded_region_ids)),
        "radius_miles": None if radius_miles is None else round(float(radius_miles), 3),
    }
    digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:20]
    return f"geo1:{digest}"
