from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from poc.sources.catalog import SourceCatalog, SourceDefinition
from poc.sources.transport import FetchResult
from .factory import create_adapter
from .models import EventCandidate, SourceIngestionMetrics
from .normalizer import normalize

FetchFn = Callable[[SourceDefinition], FetchResult]

@dataclass(frozen=True, slots=True)
class IngestionBatch:
    catalog_revision: str
    events: tuple[EventCandidate, ...]
    metrics: tuple[SourceIngestionMetrics, ...]

class EventIngestionService:
    def ingest_source(self, source: SourceDefinition, result: FetchResult, *, retrieved_at: datetime | None = None):
        retrieved_at = retrieved_at or datetime.now(timezone.utc)
        raws = create_adapter(source).parse(source, result)
        accepted: list[EventCandidate] = []
        missing_start = missing_title = missing_location = rejected = 0
        errors: list[str] = []
        for raw in raws:
            if not raw.title.strip():
                missing_title += 1
            if raw.start is None:
                missing_start += 1
            if not any((raw.venue, raw.address, raw.city, raw.latitude)):
                missing_location += 1
            try:
                accepted.append(normalize(raw, retrieved_at=retrieved_at))
            except ValueError as exc:
                rejected += 1
                errors.append(str(exc))
        return tuple(accepted), SourceIngestionMetrics(source_id=source.source_id, fetched_items=len(raws), accepted_items=len(accepted), rejected_items=rejected, missing_start=missing_start, missing_title=missing_title, missing_location=missing_location, errors=tuple(errors))

    def ingest_catalog(self, catalog: SourceCatalog, fetch: FetchFn) -> IngestionBatch:
        all_events: list[EventCandidate] = []
        metrics: list[SourceIngestionMetrics] = []
        for source in catalog.enabled_sources():
            try:
                result = fetch(source)
                events, source_metrics = self.ingest_source(source, result)
                all_events.extend(events)
                metrics.append(source_metrics)
            except Exception as exc:
                metrics.append(SourceIngestionMetrics(source_id=source.source_id, errors=(f"{type(exc).__name__}: {exc}",)))
        return IngestionBatch(catalog_revision=catalog.revision(), events=tuple(all_events), metrics=tuple(metrics))
