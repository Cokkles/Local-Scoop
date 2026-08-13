from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any


class FreshnessState(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class ProviderProvenance:
    source_id: str
    retrieved_at: datetime
    endpoints: tuple[str, ...] = field(default_factory=tuple)

    def to_contract(self) -> dict[str, Any]:
        return {"source_id": self.source_id, "retrieved_at": self.retrieved_at.isoformat(), "endpoints": list(self.endpoints)}


@dataclass(frozen=True, slots=True)
class CachePolicy:
    forecast_ttl: timedelta = timedelta(minutes=30)
    alerts_ttl: timedelta = timedelta(minutes=2)
    expire_after: timedelta = timedelta(hours=6)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
