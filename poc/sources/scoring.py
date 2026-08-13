from __future__ import annotations
from dataclasses import dataclass
from .models import SourceRecord

@dataclass(frozen=True, slots=True)
class SourceScore:
    source_id: str
    score: float
    band: str

def score_source(source: SourceRecord) -> SourceScore:
    # Authority is inverted because tier 1 is strongest.
    authority = 6 - source.authority_tier
    score = (
        authority * 0.25
        + source.structure_score * 0.25
        + source.coverage_score * 0.25
        + source.maintenance_score * 0.15
        + source.cost_score * 0.10
    )
    band = "high" if score >= 4.2 else "medium" if score >= 3.3 else "low"
    return SourceScore(source.source_id, round(score, 2), band)
