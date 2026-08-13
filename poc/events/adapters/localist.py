from __future__ import annotations
import json
from datetime import datetime
from poc.sources.catalog import SourceDefinition
from poc.sources.transport import FetchResult
from ..models import RawEvent

class LocalistAdapter:
    def parse(self, source: SourceDefinition, result: FetchResult) -> list[RawEvent]:
        payload = json.loads(result.body)
        events = []
        for wrapper in payload.get("events", []):
            event = wrapper.get("event", wrapper)
            instances = event.get("event_instances") or [{"event_instance":{"start":event.get("start"),"end":event.get("end")}}]
            for wrapped in instances:
                instance = wrapped.get("event_instance", wrapped)
                start = datetime.fromisoformat(instance["start"]) if instance.get("start") else None
                end = datetime.fromisoformat(instance["end"]) if instance.get("end") else None
                place = event.get("place") or {}
                events.append(RawEvent(source.source_id, str(instance.get("id") or event.get("id")), event.get("title") or "", start, end, venue=place.get("name") or event.get("location_name"), address=place.get("address") or event.get("address"), description=event.get("description_text") or event.get("description"), source_url=event.get("localist_url") or event.get("url") or result.url, category_hints=tuple(x.get("name") for x in (event.get("filters") or {}).get("event_types", []) if x.get("name")), raw_payload=json.dumps(event, sort_keys=True)))
        return events
