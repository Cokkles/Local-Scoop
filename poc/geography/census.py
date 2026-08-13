from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import CountyRef, GeographyLookup, Point

CENSUS_COORDINATES_URL = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"


class GeographyLookupError(RuntimeError):
    pass


Transport = Callable[[str], Mapping[str, Any]]


@dataclass(slots=True)
class CensusGeocoder:
    transport: Transport | None = None
    timeout_seconds: float = 10.0

    def lookup(self, point: Point) -> GeographyLookup:
        query = urlencode(
            {
                "x": point.longitude,
                "y": point.latitude,
                "benchmark": "Public_AR_Current",
                "vintage": "Current_Current",
                "format": "json",
            }
        )
        url = f"{CENSUS_COORDINATES_URL}?{query}"
        payload = (self.transport or self._http_get_json)(url)
        return parse_census_geography(payload, point)

    def _http_get_json(self, url: str) -> Mapping[str, Any]:
        request = Request(url, headers={"User-Agent": "Local-Scoop-POC/0.2"})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.load(response)


def parse_census_geography(payload: Mapping[str, Any], point: Point) -> GeographyLookup:
    try:
        geographies = payload["result"]["geographies"]
    except (KeyError, TypeError) as exc:
        raise GeographyLookupError("Census response did not contain geographies") from exc

    counties = _first_layer(geographies, "Counties")
    if counties is None:
        raise GeographyLookupError("Census response did not identify a county")

    state_fips = str(counties.get("STATE") or "")
    county_code = str(counties.get("COUNTY") or "")
    county_geoid = str(counties.get("GEOID") or f"{state_fips}{county_code}")
    county_name = str(counties.get("BASENAME") or counties.get("NAME") or "").strip()
    if county_name and not county_name.lower().endswith("county"):
        county_name = f"{county_name} County"

    state = _first_layer(geographies, "States") or {}
    state_name = str(state.get("NAME") or "")
    state_abbr = _state_abbreviation_from_fips(state_fips)

    place = _first_layer(geographies, "Incorporated Places")
    if place is None:
        place = _first_layer(geographies, "Census Designated Places")
    city = None
    place_geoid = None
    if place:
        city = str(place.get("BASENAME") or place.get("NAME") or "").strip()
        for suffix in (" city", " town", " village", " CDP"):
            if city.endswith(suffix):
                city = city[: -len(suffix)]
                break
        place_geoid = str(place.get("GEOID") or "") or None

    return GeographyLookup(
        point=point,
        county=CountyRef(geoid=county_geoid, name=county_name, state=state_abbr),
        state_fips=state_fips,
        state_name=state_name,
        city=city,
        place_geoid=place_geoid,
    )


def _first_layer(geographies: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    layer = geographies.get(key)
    if isinstance(layer, list) and layer and isinstance(layer[0], Mapping):
        return layer[0]
    return None


def _state_abbreviation_from_fips(state_fips: str) -> str:
    return {"37": "NC"}.get(state_fips, state_fips)
