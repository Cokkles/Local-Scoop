from __future__ import annotations

from dataclasses import dataclass

from .models import WeatherSnapshot


@dataclass(slots=True)
class MemoryWeatherCache:
    _items: dict[str, WeatherSnapshot]

    def __init__(self) -> None:
        self._items = {}

    def get(self, key: str) -> WeatherSnapshot | None:
        return self._items.get(key)

    def put(self, key: str, snapshot: WeatherSnapshot) -> None:
        self._items[key] = snapshot

    def clear(self) -> None:
        self._items.clear()


def cache_key(region_id: str) -> str:
    return f"weather:v1:{region_id}"
