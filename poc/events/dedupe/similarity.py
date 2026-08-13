from __future__ import annotations

from datetime import timedelta
from difflib import SequenceMatcher

from poc.events.models import EventCandidate
from poc.geography.distance import haversine_miles
from poc.geography.models import Point
from .normalize import content_tokens, normalize_text, normalized_venue


def text_similarity(left: str | None, right: str | None) -> float:
    a, b = normalize_text(left), normalize_text(right)
    if not a or not b:
        return 0.0
    all_tokens = content_tokens(left) | content_tokens(right)
    token_score = len(content_tokens(left) & content_tokens(right)) / len(all_tokens) if all_tokens else 0.0
    return round(max(SequenceMatcher(None, a, b).ratio(), token_score), 6)


def venue_similarity(left: str | None, right: str | None) -> float:
    return text_similarity(normalized_venue(left), normalized_venue(right))


def time_similarity(left: EventCandidate, right: EventCandidate) -> float:
    delta = abs(left.start - right.start)
    if delta <= timedelta(minutes=5): return 1.0
    if delta <= timedelta(minutes=30): return 0.9
    if delta <= timedelta(hours=1): return 0.75
    if delta <= timedelta(hours=2): return 0.45
    if delta <= timedelta(hours=4): return 0.2
    return 0.0


def geography_similarity(left: EventCandidate, right: EventCandidate) -> float:
    if None not in (left.latitude, left.longitude, right.latitude, right.longitude):
        miles = haversine_miles(Point(left.latitude, left.longitude), Point(right.latitude, right.longitude))
        if miles <= 0.10: return 1.0
        if miles <= 0.50: return 0.9
        if miles <= 2.0: return 0.55
        if miles <= 10.0: return 0.2
        return 0.0
    if left.city and right.city and left.city.casefold() == right.city.casefold():
        return 1.0
    return 0.0
