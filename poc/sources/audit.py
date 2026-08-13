from __future__ import annotations
from collections import Counter
from dataclasses import asdict
from .registry import by_adapter_family, enabled_sources, load_registry, sources_for_county
from .scoring import score_source

def build_audit() -> dict:
    raw, sources = load_registry()
    county_rows = []
    for county in raw["counties"]:
        matches = sources_for_county(sources, county["geoid"])
        primary = [s for s in matches if s.authority_tier <= 2 and s.readiness.value in {"ready","requires_key","licensed"}]
        county_rows.append({
            "geoid": county["geoid"],
            "name": county["name"],
            "role": county["role"],
            "source_count": len(matches),
            "primary_source_count": len(primary),
            "enabled_source_count": sum(s.enabled_for_phase_0_5 for s in matches),
        })
    return {
        "market": raw["market"],
        "source_count": len(sources),
        "enabled_phase_0_5_count": len(enabled_sources(sources)),
        "readiness": dict(Counter(s.readiness.value for s in sources)),
        "adapter_families": {k: [s.source_id for s in v] for k,v in by_adapter_family(sources).items()},
        "county_coverage": county_rows,
        "scores": [asdict(score_source(s)) for s in sources],
    }
