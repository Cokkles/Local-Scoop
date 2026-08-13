from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any, Iterable
from .security import ensure_no_inline_secrets, validate_public_https_url, validate_user_adapter

class SourceOrigin(StrEnum):
    BUILTIN="builtin"; SERVER="server"; USER="user"
class TrustState(StrEnum):
    CURATED="curated"; PROPOSED="proposed"; APPROVED="approved"; REJECTED="rejected"
VALID_CONTENT_TYPES={"event","news"}
def _content_types(values):
    result=tuple(dict.fromkeys(values or ("event",)))
    if not result or not set(result)<=VALID_CONTENT_TYPES: raise ValueError("unsupported content type")
    return result
@dataclass(frozen=True, slots=True)
class SourceDefinition:
    source_id:str; name:str; url:str; adapter_family:str; authority_tier:int; enabled:bool
    origin:SourceOrigin; trust_state:TrustState; config:dict[str,Any]; county_geoids:tuple[str,...]=()
    lifecycle:str="active"; secret_ref:str|None=None; content_types:tuple[str,...]=("event",)
    @classmethod
    def from_registry(cls,row):
        return cls(row["source_id"],row["name"],row["url"],row["adapter_family"],int(row["authority_tier"]),bool(row.get("enabled_for_phase_0_5",False)),SourceOrigin.BUILTIN,TrustState.CURATED,dict(row.get("adapter_config") or {}),tuple(row.get("county_geoids") or ()),row.get("readiness","candidate"),None,_content_types(row.get("content_types") or ("event",)))
class SourceCatalog:
    def __init__(self,sources=()): self._sources={s.source_id:s for s in sources}
    @classmethod
    def from_phase_0_4_registry(cls,document): return cls(SourceDefinition.from_registry(r) for r in document.get("sources",[]))
    def apply_server_overlay(self,rows):
        for row in rows:
            sid=row["source_id"]; existing=self._sources.get(sid)
            if existing:
                config=dict(existing.config); config.update(row.get("config") or {}); ensure_no_inline_secrets(config)
                url=row.get("url",existing.url); validate_public_https_url(url)
                self._sources[sid]=replace(existing,url=url,adapter_family=row.get("adapter_family",existing.adapter_family),enabled=bool(row.get("enabled",existing.enabled)),origin=SourceOrigin.SERVER,config=config,lifecycle=row.get("lifecycle",existing.lifecycle),secret_ref=row.get("secret_ref",existing.secret_ref),content_types=_content_types(row.get("content_types") or existing.content_types))
            else:
                config=dict(row.get("config") or {}); ensure_no_inline_secrets(config); validate_public_https_url(row["url"])
                self._sources[sid]=SourceDefinition(sid,row["name"],row["url"],row["adapter_family"],max(1,int(row.get("authority_tier",3))),bool(row.get("enabled",False)),SourceOrigin.SERVER,TrustState.CURATED,config,tuple(row.get("county_geoids") or ()),row.get("lifecycle","candidate"),row.get("secret_ref"),_content_types(row.get("content_types") or ("event",)))
    def propose_user_source(self,*,name,url,adapter_family,config=None,county_geoids=(),content_types=("event",)):
        validate_public_https_url(url); validate_user_adapter(adapter_family); config=dict(config or {}); ensure_no_inline_secrets(config)
        kinds=_content_types(content_types); digest=hashlib.sha256(f"{adapter_family}|{url}|{','.join(kinds)}".encode()).hexdigest()[:16]
        source=SourceDefinition(f"user:{digest}",name.strip(),url,adapter_family,4,False,SourceOrigin.USER,TrustState.PROPOSED,config,tuple(county_geoids),"candidate",None,kinds); self._sources[source.source_id]=source; return source
    def approve_user_source(self,source_id):
        source=self._sources[source_id]
        if source.origin is not SourceOrigin.USER: raise ValueError("only user-proposed sources use this approval flow")
        approved=replace(source,enabled=True,trust_state=TrustState.APPROVED); self._sources[source_id]=approved; return approved
    def enabled_sources(self,content_type=None):
        rows=(s for s in self._sources.values() if s.enabled and s.trust_state is not TrustState.REJECTED)
        if content_type is not None: rows=(s for s in rows if content_type in s.content_types)
        return tuple(rows)
    def get(self,source_id): return self._sources[source_id]
    def all_sources(self): return tuple(self._sources.values())
    def revision(self):
        payload=[{"id":s.source_id,"url":s.url,"adapter":s.adapter_family,"enabled":s.enabled,"origin":s.origin.value,"trust":s.trust_state.value,"lifecycle":s.lifecycle,"config":s.config,"content_types":s.content_types} for s in sorted(self._sources.values(),key=lambda value:value.source_id)]
        return "catalog1:"+hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()[:24]
