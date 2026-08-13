from __future__ import annotations
from datetime import datetime
from poc.sources.catalog import SourceDefinition
from poc.sources.transport import FetchResult
from ..models import RawEvent

def _value(block: str, name: str) -> str | None:
    for prefix in ('', 'ls:'):
        start=f'<{prefix}{name}>'; end=f'</{prefix}{name}>'
        if start in block and end in block:
            return block.split(start,1)[1].split(end,1)[0].strip()
    return None

class RssAtomAdapter:
    def parse(self, source: SourceDefinition, result: FetchResult) -> list[RawEvent]:
        text=result.body.decode('utf-8',errors='replace'); events=[]
        for block in text.split('<item>')[1:]:
            block=block.split('</item>',1)[0]; title=_value(block,'title') or ''; start_text=_value(block,'start')
            start=datetime.fromisoformat(start_text.replace('Z','+00:00')) if start_text else None
            events.append(RawEvent(source.source_id,_value(block,'guid') or title,title,start,venue=_value(block,'venue'),city=_value(block,'city'),state=_value(block,'state'),description=_value(block,'description'),source_url=_value(block,'link') or result.url,raw_payload=block))
        return events
