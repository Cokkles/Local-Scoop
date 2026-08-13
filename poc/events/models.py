from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass(frozen=True, slots=True)
class RawEvent:
    source_id: str
    external_id: str
    title: str
    start: datetime | None
    end: datetime | None = None
    venue: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    source_url: str | None = None
    category_hints: tuple[str, ...] = ()
    status: str = "scheduled"
    raw_payload: str = ""
    @property
    def raw_sha256(self) -> str:
        return hashlib.sha256(self.raw_payload.encode()).hexdigest()

@dataclass(frozen=True, slots=True)
class EventCandidate:
    event_id: str
    source_id: str
    external_id: str
    title: str
    start: datetime
    end: datetime | None
    venue: str | None
    address: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    latitude: float | None
    longitude: float | None
    description: str | None
    source_url: str | None
    category_hints: tuple[str, ...]
    status: str
    retrieved_at: datetime
    raw_sha256: str
    def to_contract(self) -> dict[str, Any]:
        geography = {"venue": self.venue, "address": self.address, "city": self.city, "state": self.state, "postal_code": self.postal_code, "latitude": self.latitude, "longitude": self.longitude}
        return {"schema_version":"1.0","event_id":self.event_id,"title":self.title,"start_time":self.start.isoformat(),"end_time":self.end.isoformat() if self.end else None,"geography":geography,"category":self.category_hints[0] if self.category_hints else "other","category_hints":list(self.category_hints),"status":self.status,"description":self.description,"provenance":[{"source_id":self.source_id,"external_id":self.external_id,"url":self.source_url,"retrieved_at":self.retrieved_at.isoformat(),"raw_sha256":self.raw_sha256}]}

@dataclass(frozen=True, slots=True)
class SourceIngestionMetrics:
    source_id: str
    fetched_items: int = 0
    accepted_items: int = 0
    rejected_items: int = 0
    missing_start: int = 0
    missing_title: int = 0
    missing_location: int = 0
    errors: tuple[str, ...] = field(default_factory=tuple)
