from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO

from .models import CountyRef


@dataclass(frozen=True, slots=True)
class AdjacencyRecord:
    county_name: str
    county_geoid: str
    neighbor_name: str
    neighbor_geoid: str
    shared_boundary_m: int | None


class CountyAdjacencyIndex:
    def __init__(self, records: list[AdjacencyRecord], *, vintage: str) -> None:
        self.vintage = vintage
        self._neighbors: dict[str, list[AdjacencyRecord]] = {}
        for record in records:
            if not record.neighbor_geoid or record.county_geoid == record.neighbor_geoid:
                continue
            self._neighbors.setdefault(record.county_geoid, []).append(record)

    @classmethod
    def from_pipe_text(cls, text: str, *, vintage: str) -> "CountyAdjacencyIndex":
        reader = csv.DictReader(StringIO(text), delimiter="|")
        records: list[AdjacencyRecord] = []
        for row in reader:
            neighbor_geoid = (row.get("Neighbor GEOID") or "").strip()
            if not neighbor_geoid:
                continue
            length_raw = (row.get("Length") or "").strip()
            records.append(
                AdjacencyRecord(
                    county_name=(row.get("County Name") or "").strip(),
                    county_geoid=(row.get("County GEOID") or "").strip(),
                    neighbor_name=(row.get("Neighbor Name") or "").strip(),
                    neighbor_geoid=neighbor_geoid,
                    shared_boundary_m=int(length_raw) if length_raw else None,
                )
            )
        return cls(records, vintage=vintage)

    def neighbors(self, county_geoid: str) -> tuple[CountyRef, ...]:
        rows = sorted(self._neighbors.get(county_geoid, []), key=lambda x: x.neighbor_geoid)
        return tuple(
            CountyRef(
                geoid=row.neighbor_geoid,
                name=_county_name(row.neighbor_name),
                state=_state_abbreviation(row.neighbor_name),
                shared_boundary_m=row.shared_boundary_m,
            )
            for row in rows
        )


def _county_name(value: str) -> str:
    return value.rsplit(",", 1)[0].strip()


def _state_abbreviation(value: str) -> str:
    parts = value.rsplit(",", 1)
    return parts[1].strip() if len(parts) == 2 else ""
