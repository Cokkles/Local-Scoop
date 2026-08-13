from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from .models import Point

EARTH_RADIUS_MILES = 3958.7613


def haversine_miles(a: Point, b: Point) -> float:
    """Great-circle distance between two WGS84-style latitude/longitude points."""
    lat1, lon1, lat2, lon2 = map(
        radians, (a.latitude, a.longitude, b.latitude, b.longitude)
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * asin(sqrt(h))


def within_radius(origin: Point, candidate: Point, radius_miles: float) -> bool:
    if radius_miles < 0:
        raise ValueError("radius_miles must be non-negative")
    return haversine_miles(origin, candidate) <= radius_miles
