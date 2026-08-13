from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

class MatchDisposition(StrEnum):
    AUTO_MERGE = "auto_merge"
    PROBABLE_DUPLICATE = "probable_duplicate"
    REVIEW = "review"
    UNRELATED = "unrelated"
    CONFLICT = "conflict"

@dataclass(frozen=True, slots=True)
class MatchFeatures:
    title: float
    time: float
    venue: float
    geography: float
    description: float
    same_source_external_id: bool = False
    hard_conflicts: tuple[str, ...] = ()
    @property
    def weighted_score(self) -> float:
        return round(self.title*.35 + self.time*.25 + self.venue*.15 + self.geography*.15 + self.description*.10, 6)

@dataclass(frozen=True, slots=True)
class MatchDecision:
    left_id: str
    right_id: str
    disposition: MatchDisposition
    score: float
    features: MatchFeatures
    reasons: tuple[str, ...] = ()
    def to_contract(self) -> dict[str, Any]:
        return {"left_id":self.left_id,"right_id":self.right_id,"disposition":self.disposition.value,"score":self.score,"features":{"title":self.features.title,"time":self.features.time,"venue":self.features.venue,"geography":self.features.geography,"description":self.features.description,"same_source_external_id":self.features.same_source_external_id,"hard_conflicts":list(self.features.hard_conflicts)},"reasons":list(self.reasons)}
