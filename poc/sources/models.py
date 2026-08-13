from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

class Readiness(StrEnum):
    READY = "ready"
    CANDIDATE = "candidate"
    REQUIRES_KEY = "requires_key"
    LICENSED = "licensed"
    DEFERRED = "deferred"

@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_id: str
    name: str
    authority_tier: int
    publisher_type: str
    url: str
    adapter_family: str
    ingestion_methods: tuple[str, ...]
    readiness: Readiness
    access: str
    enabled_for_phase_0_5: bool
    county_geoids: tuple[str, ...]
    localities: tuple[str, ...]
    coverage_tags: tuple[str, ...]
    structure_score: int
    coverage_score: int
    maintenance_score: int
    cost_score: int
    notes: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SourceRecord":
        tier = int(data["authority_tier"])
        if tier < 1 or tier > 5:
            raise ValueError("authority_tier must be between 1 and 5")
        scores = {k:int(data[k]) for k in ("structure_score","coverage_score","maintenance_score","cost_score")}
        if any(v < 1 or v > 5 for v in scores.values()):
            raise ValueError("source scores must be between 1 and 5")
        return cls(
            source_id=str(data["source_id"]), name=str(data["name"]), authority_tier=tier,
            publisher_type=str(data["publisher_type"]), url=str(data["url"]),
            adapter_family=str(data["adapter_family"]),
            ingestion_methods=tuple(data["ingestion_methods"]), readiness=Readiness(data["readiness"]),
            access=str(data["access"]), enabled_for_phase_0_5=bool(data["enabled_for_phase_0_5"]),
            county_geoids=tuple(data["county_geoids"]), localities=tuple(data.get("localities", [])),
            coverage_tags=tuple(data.get("coverage_tags", [])), notes=str(data.get("notes","")), **scores
        )
