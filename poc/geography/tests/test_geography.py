from __future__ import annotations

import json
from pathlib import Path

import pytest

from poc.geography.adjacency import CountyAdjacencyIndex
from poc.geography.census import CensusGeocoder, GeographyLookupError, parse_census_geography
from poc.geography.distance import haversine_miles, within_radius
from poc.geography.models import CoverageMode, Point
from poc.geography.service import GeographyService, deterministic_region_id

DATA = Path(__file__).parents[1] / "data"
RALEIGH = Point(latitude=35.7796, longitude=-78.6382)
DURHAM = Point(latitude=35.9940, longitude=-78.8986)


def fixture_payload() -> dict:
    return json.loads((DATA / "census_raleigh_fixture.json").read_text())


def adjacency() -> CountyAdjacencyIndex:
    return CountyAdjacencyIndex.from_pipe_text(
        (DATA / "county_adjacency_wake_2025.txt").read_text(), vintage="2025"
    )


def test_census_parser_resolves_raleigh_wake() -> None:
    result = parse_census_geography(fixture_payload(), RALEIGH)
    assert result.city == "Raleigh"
    assert result.county.geoid == "37183"
    assert result.county.name == "Wake County"
    assert result.county.region_id == "us:county:37183"
    assert result.state_name == "North Carolina"


def test_census_geocoder_builds_coordinate_request() -> None:
    seen: list[str] = []

    def transport(url: str) -> dict:
        seen.append(url)
        return fixture_payload()

    result = CensusGeocoder(transport=transport).lookup(RALEIGH)
    assert result.county.geoid == "37183"
    assert "benchmark=Public_AR_Current" in seen[0]
    assert "vintage=Current_Current" in seen[0]
    assert "x=-78.6382" in seen[0]
    assert "y=35.7796" in seen[0]


def test_census_parser_rejects_missing_county() -> None:
    with pytest.raises(GeographyLookupError):
        parse_census_geography({"result": {"geographies": {}}}, RALEIGH)


def test_wake_has_seven_2025_neighbors_and_preserves_point_touch() -> None:
    neighbors = adjacency().neighbors("37183")
    assert [x.geoid for x in neighbors] == [
        "37037", "37063", "37069", "37077", "37085", "37101", "37127"
    ]
    assert next(x for x in neighbors if x.geoid == "37127").shared_boundary_m == 0


def test_adjacent_county_region_contains_home_plus_seven_neighbors() -> None:
    geocoder = CensusGeocoder(transport=lambda _: fixture_payload())
    region = GeographyService(geocoder=geocoder, adjacency=adjacency()).build_region(RALEIGH)
    assert region.city == "Raleigh"
    assert region.timezone == "America/New_York"
    assert region.home_region_id == "us:county:37183"
    assert len(region.included_regions) == 8
    assert region.adjacency_vintage == "2025"
    assert region.to_contract()["coverage_mode"] == "adjacent_counties"


def test_exclusion_changes_region_identity_and_filters_county() -> None:
    geocoder = CensusGeocoder(transport=lambda _: fixture_payload())
    service = GeographyService(geocoder=geocoder, adjacency=adjacency())
    full = service.build_region(RALEIGH)
    filtered = service.build_region(RALEIGH, exclude_region_ids=["us:county:37127"])
    assert full.region_id != filtered.region_id
    assert "37127" not in {x.geoid for x in filtered.included_regions}


def test_region_id_is_order_independent() -> None:
    a = deterministic_region_id(
        home_county_geoid="37183",
        coverage_mode=CoverageMode.CUSTOM,
        included_geoids=["37183", "37063", "37037"],
        excluded_region_ids=["us:county:37127", "us:county:37069"],
        radius_miles=None,
    )
    b = deterministic_region_id(
        home_county_geoid="37183",
        coverage_mode=CoverageMode.CUSTOM,
        included_geoids=["37037", "37183", "37063"],
        excluded_region_ids=["us:county:37069", "us:county:37127"],
        radius_miles=None,
    )
    assert a == b


def test_radius_mode_requires_positive_radius() -> None:
    geocoder = CensusGeocoder(transport=lambda _: fixture_payload())
    service = GeographyService(geocoder=geocoder, adjacency=adjacency())
    with pytest.raises(ValueError):
        service.build_region(RALEIGH, coverage_mode=CoverageMode.RADIUS)


def test_haversine_raleigh_to_durham_is_reasonable() -> None:
    distance = haversine_miles(RALEIGH, DURHAM)
    assert 20 <= distance <= 25
    assert within_radius(RALEIGH, DURHAM, 25)
    assert not within_radius(RALEIGH, DURHAM, 15)


def test_invalid_coordinates_are_rejected() -> None:
    with pytest.raises(ValueError):
        Point(latitude=91, longitude=-78)
    with pytest.raises(ValueError):
        Point(latitude=35, longitude=-181)
