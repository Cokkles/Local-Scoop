from __future__ import annotations
from datetime import datetime
from html.parser import HTMLParser
from poc.sources.catalog import SourceDefinition
from poc.sources.transport import FetchResult
from ..models import RawEvent

class StructuredHtmlCardAdapter(HTMLParser):
    def parse(self, source: SourceDefinition, result: FetchResult) -> list[RawEvent]:
        self.source=source; self.result=result; self.events=[]; self.feed(result.body.decode('utf-8',errors='replace')); return self.events
    def handle_starttag(self, tag, attrs):
        row=dict(attrs)
        if row.get('data-local-scoop-event')!='1': return
        start=datetime.fromisoformat(row['data-start']) if row.get('data-start') else None
        self.events.append(RawEvent(self.source.source_id,row.get('data-event-id') or row.get('data-title',''),row.get('data-title',''),start,city=row.get('data-city'),state=row.get('data-state'),source_url=row.get('data-url') or self.result.url,raw_payload=str(row)))
