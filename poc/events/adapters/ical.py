from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo
from poc.sources.catalog import SourceDefinition
from poc.sources.transport import FetchResult
from ..models import RawEvent

def _unfold(text: str) -> list[str]:
    lines=[]
    for raw in text.replace("\r\n","\n").split("\n"):
        if raw.startswith((" ","\t")) and lines: lines[-1]+=raw[1:]
        else: lines.append(raw)
    return lines

def _parse_dt(name: str, value: str, default_tz: str) -> datetime:
    tzid=default_tz
    for param in name.split(";")[1:]:
        if param.startswith("TZID="): tzid=param.split("=",1)[1]
    if len(value)==8 and value.isdigit():
        d=datetime.strptime(value,"%Y%m%d").date(); return datetime.combine(d,time.min,ZoneInfo(tzid))
    if value.endswith("Z"): return datetime.strptime(value,"%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
    return datetime.strptime(value,"%Y%m%dT%H%M%S").replace(tzinfo=ZoneInfo(tzid))

def _fallback_id(title: str, start: datetime | None) -> str:
    import hashlib
    return hashlib.sha256(f"{title}|{start}".encode()).hexdigest()[:20]

class ICalendarAdapter:
    def parse(self, source: SourceDefinition, result: FetchResult) -> list[RawEvent]:
        text=result.body.decode("utf-8-sig",errors="replace"); events=[]; current=None; default_tz=source.config.get("timezone","America/New_York")
        for line in _unfold(text):
            if line=="BEGIN:VEVENT": current=[]; continue
            if line=="END:VEVENT" and current is not None:
                def get(prefix):
                    for key,val in current:
                        if key.split(";",1)[0]==prefix: return key,val
                    return None
                start_item=get("DTSTART"); end_item=get("DTEND")
                start=_parse_dt(*start_item,default_tz) if start_item else None; end=_parse_dt(*end_item,default_tz) if end_item else None
                val=lambda key: (get(key) or (None,None))[1]
                events.append(RawEvent(source.source_id,val("UID") or _fallback_id(val("SUMMARY") or "",start),val("SUMMARY") or "",start,end,venue=val("LOCATION"),description=val("DESCRIPTION"),source_url=val("URL") or result.url,category_hints=tuple(filter(None,(val("CATEGORIES") or "").split(","))),raw_payload=text))
                current=None; continue
            if current is not None and ":" in line:
                key,val=line.split(":",1); current.append((key,val.replace("\\n","\n").replace("\\,",",")))
        return events
