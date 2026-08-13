from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from .models import EventCandidate, RawEvent


def normalize(raw: RawEvent, *, retrieved_at: datetime | None = None) -> EventCandidate:
    title = " ".join(raw.title.split())
    if not title:
        raise ValueError("event title is required")
    if raw.start is None:
        raise ValueError("event start is required")
    retrieved_at = retrieved_at or datetime.now(timezone.utc)
    seed = f"{raw.source_id}|{raw.external_id}|{raw.start.isoformat()}"
    event_id = "candidate1:" + hashlib.sha256(seed.encode()).hexdigest()[:24]
    return EventCandidate(event_id=event_id, source_id=raw.source_id, external_id=raw.external_id, title=title, start=raw.start, end=raw.end, venue=raw.venue, address=raw.address, city=raw.city, state=raw.state, postal_code=raw.postal_code, latitude=raw.latitude, longitude=raw.longitude, description=raw.description, source_url=raw.source_url, category_hints=raw.category_hints, status=raw.status, retrieved_at=retrieved_at, raw_sha256=raw.raw_sha256)
