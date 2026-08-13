from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from poc.geography.models import Point

DATA = Path(__file__).parents[1] / "data"
POINT = Point(35.7796, -78.6382)
REGION_ID = "geo1:4b213a0b9c466697fbd3"
T0 = datetime(2026, 8, 13, 17, 40, tzinfo=timezone.utc)


def load(name: str):
    return json.loads((DATA / name).read_text())


class Router:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str]]] = []
        self.fail_nws_forecast = False
        self.fail_open_meteo = False
        self.fail_alerts = False

    def nws(self, url: str, headers: dict[str, str]):
        self.calls.append((url, headers))
        if "/alerts/active?" in url:
            if self.fail_alerts:
                raise OSError("alerts unavailable")
            return load("nws_alerts.json")
        if self.fail_nws_forecast:
            raise OSError("forecast unavailable")
        if "/points/" in url:
            return load("nws_points.json")
        if url.endswith("/stations"):
            return load("nws_stations.json")
        if url.endswith("/observations/latest"):
            return load("nws_observation.json")
        if url.endswith("/forecast/hourly"):
            return load("nws_hourly.json")
        if url.endswith("/forecast"):
            return load("nws_forecast.json")
        raise AssertionError(url)

    def open_meteo(self, url: str, headers: dict[str, str]):
        self.calls.append((url, headers))
        if self.fail_open_meteo:
            raise OSError("detail unavailable")
        return load("open_meteo.json")


class Clock:
    def __init__(self, value: datetime) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value

    def advance(self, **kwargs) -> None:
        self.value += timedelta(**kwargs)
