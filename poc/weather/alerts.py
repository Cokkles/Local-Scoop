from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class WeatherAlert:
    alert_id: str
    event: str
    headline: str | None = None
    severity: str | None = None
    urgency: str | None = None
    certainty: str | None = None
    status: str | None = None
    message_type: str | None = None
    area_description: str | None = None
    sent_at: datetime | None = None
    onset_at: datetime | None = None
    effective_at: datetime | None = None
    expires_at: datetime | None = None
    description: str | None = None
    instruction: str | None = None
    sender_name: str | None = None
    source_url: str | None = None
    source_ids: tuple[str, ...] = ("nws",)

    def to_contract(self) -> dict[str, Any]:
        iso = lambda value: value.isoformat() if value else None
        return {
            "alert_id": self.alert_id, "event": self.event, "headline": self.headline,
            "severity": self.severity, "urgency": self.urgency, "certainty": self.certainty,
            "status": self.status, "message_type": self.message_type, "area_description": self.area_description,
            "sent_at": iso(self.sent_at), "onset_at": iso(self.onset_at), "effective_at": iso(self.effective_at),
            "expires_at": iso(self.expires_at), "description": self.description, "instruction": self.instruction,
            "sender_name": self.sender_name, "source_url": self.source_url, "source_ids": list(self.source_ids),
        }
