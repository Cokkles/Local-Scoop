from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adjacency import CountyAdjacencyIndex
from .census import CensusGeocoder
from .models import CoverageMode, Point
from .service import GeographyService

DATA = Path(__file__).with_name("data")


def main() -> int:
    parser = argparse.ArgumentParser(description="Local Scoop Phase 0.2 geography POC")
    parser.add_argument("--lat", type=float, default=35.7796)
    parser.add_argument("--lon", type=float, default=-78.6382)
    parser.add_argument(
        "--mode",
        choices=[x.value for x in CoverageMode],
        default=CoverageMode.ADJACENT_COUNTIES.value,
    )
    parser.add_argument("--radius", type=float)
    parser.add_argument(
        "--offline-fixture",
        action="store_true",
        help="Use the bundled Raleigh/Wake Census response instead of a live Census request.",
    )
    args = parser.parse_args()

    adjacency = CountyAdjacencyIndex.from_pipe_text(
        (DATA / "county_adjacency_wake_2025.txt").read_text(), vintage="2025"
    )
    if args.offline_fixture:
        payload = json.loads((DATA / "census_raleigh_fixture.json").read_text())
        geocoder = CensusGeocoder(transport=lambda _: payload)
    else:
        geocoder = CensusGeocoder()

    region = GeographyService(geocoder=geocoder, adjacency=adjacency).build_region(
        Point(args.lat, args.lon),
        coverage_mode=CoverageMode(args.mode),
        radius_miles=args.radius,
    )
    print(json.dumps(region.to_contract(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
