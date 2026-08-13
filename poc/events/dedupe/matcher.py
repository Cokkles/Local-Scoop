from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
from poc.events.models import EventCandidate
from .models import MatchDecision, MatchDisposition, MatchFeatures
from .similarity import geography_similarity, text_similarity, time_similarity, venue_similarity

@dataclass(frozen=True, slots=True)
class MatchThresholds:
    auto_merge: float = 0.88
    probable: float = 0.76
    review: float = 0.58

class EventMatcher:
    def __init__(self, thresholds: MatchThresholds | None = None) -> None:
        self.thresholds = thresholds or MatchThresholds()
    def compare(self, left: EventCandidate, right: EventCandidate) -> MatchDecision:
        same = left.source_id == right.source_id and left.external_id == right.external_id
        delta = abs(left.start - right.start)
        hard = []
        if left.start.date() != right.start.date() and delta > timedelta(hours=6): hard.append("different_calendar_date")
        elif delta > timedelta(hours=4): hard.append("start_time_difference_gt_4h")
        geo = geography_similarity(left, right)
        if left.city and right.city and left.city.casefold() != right.city.casefold() and geo == 0: hard.append("different_city")
        f = MatchFeatures(text_similarity(left.title,right.title),time_similarity(left,right),venue_similarity(left.venue,right.venue),geo,text_similarity(left.description,right.description),same,tuple(hard))
        score = 1.0 if same and not hard else f.weighted_score
        if hard: d,r = MatchDisposition.CONFLICT,tuple(hard)
        elif same: d,r = MatchDisposition.AUTO_MERGE,("same_source_external_id",)
        elif f.title < 0.45: d,r = MatchDisposition.UNRELATED,("low_title_similarity",)
        elif score >= self.thresholds.auto_merge and f.time >= 0.75 and (f.venue >= 0.55 or f.geography >= 0.55): d,r = MatchDisposition.AUTO_MERGE,("high_multifield_similarity",)
        elif score >= self.thresholds.probable: d,r = MatchDisposition.PROBABLE_DUPLICATE,("probable_duplicate_score",)
        elif score >= self.thresholds.review: d,r = MatchDisposition.REVIEW,("ambiguous_similarity",)
        else: d,r = MatchDisposition.UNRELATED,("below_review_threshold",)
        return MatchDecision(left.event_id,right.event_id,d,round(score,6),f,r)
