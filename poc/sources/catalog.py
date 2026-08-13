from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any, Iterable

from .security import ensure_no_inline_secrets, validate_public_https_url, validate_user_adapter


class SourceOrigin(StrEnum):
    BUILTIN = "builtin"
    SERVER = "server"
    USER = "user"


class TrustState(StrEnum):
    CURATED = "curated"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class SourceDefinition:
    source_id: str
    name: str
    url: str
    adapter_family: str
    authority_tier: int
    enabled: bool
    origin: SourceOrigin
    trust_state: TrustState
    config: dict[str, Any]
    county_geoids: tuple[str, ...] = ()
    lifecycle: str = "active"
    secret_ref: str | None = None

    @classmethod
    def from_registry(cls, row: dict[str, Any]) -> "SourceDefinition":
        config = dict(row.get("adapter_config") or {})
        return cls(source_id=row["source_id"], name=row["name"], url=row["url"], adapter_family=row["adapter_family"], authority_tier=int(row["authority_tier"]), enabled=bool(row.get("enabled_for_phase_0_5", False)), origin=SourceOrigin.BUILTIN, trust_state=TrustState.CURATED, config=config, county_geoids=tuple(row.get("county_geoids") or ()), lifecycle=row.get("readiness", "candidate"))


class SourceCatalog:
    def __init__(self, sources: Iterable[SourceDefinition] = ()) -> None:
        self._sources = {source.source_id: source for source in sources}

    @classmethod
    def from_phase_0_4_registry(cls, document: dict[str, Any]) -> "SourceCatalog":
        return cls(SourceDefinition.from_registry(row) for row in document.get("sources", []))

    def apply_server_overlay(self, rows: Iterable[dict[str, Any]]) -> None:
        for row in rows:
            source_id = row["source_id"]
            existing = self._sources.get(source_id)
            if existing:
                config = dict(existing.config); config.update(row.get("config") or {})
                ensure_no_inline_secrets(config)
                url = row.get("url", existing.url); validate_public_https_url(url)
                self._sources[source_id] = replace(existing, url=url, adapter_family=row.get("adapter_family", existing.adapter_family), enabled=bool(row.get("enabled", existing.enabled)), origin=SourceOrigin.SERVER, config=config, lifecycle=row.get("lifecycle", existing.lifecycle), secret_ref=row.get("secret_ref", existing.secret_ref))
            else:
                config = dict(row.get("config") or {}); ensure_no_inline_secrets(config); validate_public_https_url(row["url"])
                self._sources[source_id] = SourceDefinition(source_id=source_id, name=row["name"], url=row["url"], adapter_family=row["adapter_family"], authority_tier=max(1, int(row.get("authority_tier", 3))), enabled=bool(row.get("enabled", False)), origin=SourceOrigin.SERVER, trust_state=TrustState.CURATED, config=config, county_geoids=tuple(row.get("county_geoids") or ()), lifecycle=row.get("lifecycle", "candidate"), secret_ref=row.get("secret_ref"))

    def propose_user_source(self, *, name: str, url: str, adapter_family: str, config: dict[str, Any] | None = None, county_geoids: Iterable[str] = ()) -> SourceDefinition:
        validate_public_https_url(url); validate_user_adapter(adapter_family)
        config = dict(config or {}); ensure_no_inline_secrets(config)
        digest = hashlib.sha256(f"{adapter_family}|{url}".encode()).hexdigest()[:16]
        source = SourceDefinition(source_id=f"user:{digest}", name=name.strip(), url=url, adapter_family=adapter_family, authority_tier=4, enabled=False, origin=SourceOrigin.USER, trust_state=TrustState.PROPOSED, config=config, county_geoids=tuple(county_geoids), lifecycle="candidate")
        self._sources[source.source_id] = source
        return source

    def approve_user_source(self, source_id: str) -> SourceDefinition:
        source = self._sources[source_id]
        if source.origin is not SourceOrigin.USER: raise ValueError("only user-proposed sources use this approval flow")
        approved = replace(source, enabled=True, trust_state=TrustState.APPROVED); self._sources[source_id] = approved; return approved

    def enabled_sources(self) -> tuple[SourceDefinition, ...]:
        return tuple(s for s in self._sources.values() if s.enabled and s.trust_state is not TrustState.REJECTED)

    def get(self, source_id: str) -> SourceDefinition: return self._sources[source_id]
    def all_sources(self) -> tuple[SourceDefinition, ...]: return tuple(self._sources.values())

    def revision(self) -> str:
        payload = [{"id":s.source_id,"url":s.url,"adapter":s.adapter_family,"enabled":s.enabled,"origin":s.origin.value,"trust":s.trust_state.value,"lifecycle":s.lifecycle,"config":s.config} for s in sorted(self._sources.values(), key=lambda value: value.source_id)]
        return "catalog1:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:24]
