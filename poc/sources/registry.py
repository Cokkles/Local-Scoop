from __future__ import annotations
import json
from pathlib import Path
from .models import Readiness, SourceRecord

DEFAULT_REGISTRY = Path(__file__).with_name("data") / "source_registry.json"

def load_registry(path: Path = DEFAULT_REGISTRY) -> tuple[dict, tuple[SourceRecord, ...]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    sources = tuple(SourceRecord.from_dict(item) for item in raw["sources"])
    validate_registry(raw, sources)
    return raw, sources

def validate_registry(raw: dict, sources: tuple[SourceRecord, ...]) -> None:
    ids = [s.source_id for s in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("source_id values must be unique")
    county_geoids = {c["geoid"] for c in raw["counties"]}
    if len(county_geoids) != len(raw["counties"]):
        raise ValueError("county GEOIDs must be unique")
    for source in sources:
        if not source.url.startswith("https://"):
            raise ValueError(f"{source.source_id}: url must use https")
        unknown = set(source.county_geoids) - county_geoids
        if unknown:
            raise ValueError(f"{source.source_id}: unknown county GEOIDs {sorted(unknown)}")
        if source.enabled_for_phase_0_5 and source.readiness not in {Readiness.READY, Readiness.REQUIRES_KEY}:
            raise ValueError(f"{source.source_id}: enabled source is not ingestion-ready")
        if source.adapter_family == "civicengage" and "ical" not in source.ingestion_methods:
            raise ValueError(f"{source.source_id}: CivicEngage source should preserve iCalendar capability")

def sources_for_county(sources: tuple[SourceRecord, ...], geoid: str) -> tuple[SourceRecord, ...]:
    return tuple(s for s in sources if geoid in s.county_geoids)

def enabled_sources(sources: tuple[SourceRecord, ...]) -> tuple[SourceRecord, ...]:
    return tuple(s for s in sources if s.enabled_for_phase_0_5)

def by_adapter_family(sources: tuple[SourceRecord, ...]) -> dict[str, tuple[SourceRecord, ...]]:
    families: dict[str, list[SourceRecord]] = {}
    for source in sources:
        families.setdefault(source.adapter_family, []).append(source)
    return {k: tuple(v) for k, v in sorted(families.items())}
