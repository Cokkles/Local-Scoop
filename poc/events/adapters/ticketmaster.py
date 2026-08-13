from __future__ import annotations
import json
from datetime import datetime
from poc.sources.catalog import SourceDefinition
from poc.sources.transport import FetchResult
from ..models import RawEvent

class TicketmasterAdapter:
    def parse(self, source: SourceDefinition, result: FetchResult) -> list[RawEvent]:
        payload=json.loads(result.body); events=[]
        for event in (payload.get("_embedded") or {}).get("events",[]):
            dates=event.get("dates") or {}; start_data=dates.get("start") or {}; text=start_data.get("dateTime")
            start=datetime.fromisoformat(text.replace("Z","+00:00")) if text else None
            venue=(((event.get("_embedded") or {}).get("venues") or [{}])[0]); location=venue.get("location") or {}; hints=[]
            classifications=event.get("classifications") or []
            if classifications:
                first=classifications[0]
                for key in ("segment","genre","subGenre"):
                    if (first.get(key) or {}).get("name"): hints.append(first[key]["name"])
            events.append(RawEvent(source.source_id,str(event.get("id")),event.get("name") or "",start,venue=venue.get("name"),address=(venue.get("address") or {}).get("line1"),city=(venue.get("city") or {}).get("name"),state=(venue.get("state") or {}).get("stateCode"),postal_code=venue.get("postalCode"),latitude=float(location["latitude"]) if location.get("latitude") else None,longitude=float(location["longitude"]) if location.get("longitude") else None,source_url=event.get("url") or result.url,category_hints=tuple(hints),status=(dates.get("status") or {}).get("code") or "scheduled",raw_payload=json.dumps(event,sort_keys=True)))
        return events
